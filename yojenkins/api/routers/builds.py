"""Builds API routes."""

from fastapi import APIRouter, Depends, Query
from starlette.concurrency import run_in_threadpool

from yojenkins.api.dependencies import get_yo_jenkins

router = APIRouter()


@router.get("/info")
async def build_info(
    url: str = Query(..., description="Build URL"),
    yj=Depends(get_yo_jenkins),
):
    """Get build information."""
    return await run_in_threadpool(yj.build.info, build_url=url)


@router.get("/logs")
async def build_logs(
    url: str = Query(..., description="Build URL"),
    yj=Depends(get_yo_jenkins),
):
    """Get build console logs."""
    # /consoleText is the Jenkins REST endpoint for raw plaintext build logs.
    request_url = f'{url.strip("/")}/consoleText'
    # is_endpoint=False (url is full, don't prepend base),
    # json_content=False (response is plaintext, not JSON)
    content, _, success = await run_in_threadpool(
        yj.rest.request, request_url, 'get', False, False
    )
    if not success:
        return {"logs": "", "error": "Failed to fetch logs"}
    return {"logs": content}


@router.get("/stages")
async def build_stages(
    url: str = Query(..., description="Build URL"),
    yj=Depends(get_yo_jenkins),
):
    """Get build stages."""
    stages, stage_names = await run_in_threadpool(yj.build.stage_list, build_url=url)
    return {"stages": stages, "stage_names": stage_names}
