"""WebSocket endpoint for real-time build monitoring."""

import asyncio
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool

from yojenkins.api.dependencies import _decode_token, _sessions

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket('/build-monitor')
async def build_monitor(
    websocket: WebSocket,
    build_url: str = Query(...),
    # WebSocket connections from browsers can't set Authorization headers,
    # so the JWT is passed as a query param. Tradeoff: token may appear in
    # server access logs. Mitigated by short TTL and HTTPS in production.
    token: str = Query(...),
):
    """WebSocket endpoint for live build monitoring.

    Connect with: ws://host/api/ws/build-monitor?build_url=<URL>&token=<JWT>
    """
    # Authenticate via token query param
    user_id = _decode_token(token)
    if not user_id or user_id not in _sessions:
        await websocket.close(code=4001, reason='Unauthorized')
        return

    yj, _ = _sessions[user_id]

    await websocket.accept()
    try:
        while True:
            info = await run_in_threadpool(yj.build.info, build_url=build_url)

            try:
                stages, stage_names = await run_in_threadpool(yj.build.stage_list, build_url=build_url)
            except Exception:
                # Stages may not exist for non-pipeline builds — treat as empty
                stages, stage_names = [], []

            await websocket.send_json(
                {
                    'type': 'build_update',
                    'info': info,
                    'stages': stages,
                    'stage_names': stage_names,
                }
            )

            result_text = info.get('resultText', '')
            if result_text and result_text not in ('RUNNING', 'IN_PROGRESS'):
                await websocket.send_json(
                    {
                        'type': 'build_complete',
                        'info': info,
                    }
                )
                break

            await asyncio.sleep(5)  # Poll interval — light on Jenkins API load
    except WebSocketDisconnect:
        logger.debug('WebSocket client disconnected')
    except Exception as exc:
        logger.error(f'WebSocket error: {exc}')
        await websocket.close(code=1011, reason=str(exc))
