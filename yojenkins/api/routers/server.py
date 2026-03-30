"""Server API routes."""

from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from yojenkins.api.dependencies import get_yo_jenkins

router = APIRouter()


@router.get('/info')
async def server_info(yj=Depends(get_yo_jenkins)):
    """Get server information."""
    return await run_in_threadpool(yj.server.info)


@router.get('/people')
async def server_people(yj=Depends(get_yo_jenkins)):
    """Get list of people/users on the server."""
    people, people_list = await run_in_threadpool(yj.server.people)
    return {'people': people, 'people_list': people_list}


@router.get('/queue')
async def server_queue(yj=Depends(get_yo_jenkins)):
    """Get the server build queue."""
    return await run_in_threadpool(yj.server.queue_info)
