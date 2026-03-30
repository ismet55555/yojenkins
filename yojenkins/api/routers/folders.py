"""Folders API routes."""

from fastapi import APIRouter, Depends, Query
from starlette.concurrency import run_in_threadpool

from yojenkins.api.dependencies import get_yo_jenkins

router = APIRouter()


@router.get('/search')
async def search_folders(
    pattern: str = Query('.*', max_length=500, description='REGEX pattern to search for'),
    depth: int = Query(4, ge=1, le=10, description='Search depth'),
    yj=Depends(get_yo_jenkins),
):
    """Search for folders matching a REGEX pattern."""
    results, urls = await run_in_threadpool(
        yj.folder.search,
        search_pattern=pattern,
        folder_depth=depth,
    )
    return {'results': results, 'urls': urls}


@router.get('/info')
async def folder_info(
    folder: str = Query(..., description='Folder name or URL'),
    yj=Depends(get_yo_jenkins),
):
    """Get folder information."""
    from yojenkins.utility.utility import is_full_url

    if is_full_url(folder):
        return await run_in_threadpool(yj.folder.info, folder_url=folder)
    return await run_in_threadpool(yj.folder.info, folder_name=folder)


@router.get('/jobs')
async def folder_jobs(
    folder: str = Query(..., description='Folder name or URL'),
    yj=Depends(get_yo_jenkins),
):
    """List all jobs in a folder."""
    from yojenkins.utility.utility import is_full_url

    if is_full_url(folder):
        jobs, urls = await run_in_threadpool(yj.folder.jobs_list, folder_url=folder)
    else:
        jobs, urls = await run_in_threadpool(yj.folder.jobs_list, folder_name=folder)
    return {'jobs': jobs, 'urls': urls}
