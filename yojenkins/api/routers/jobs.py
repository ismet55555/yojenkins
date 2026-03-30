"""Jobs API routes."""

from fastapi import APIRouter, Depends, Query
from starlette.concurrency import run_in_threadpool

from yojenkins.api.dependencies import get_yo_jenkins, validate_jenkins_url

router = APIRouter()


@router.get('/search')
async def search_jobs(
    pattern: str = Query(..., max_length=500, description='REGEX pattern to search for'),
    folder: str = Query('', description='Folder to search within'),
    depth: int = Query(4, ge=1, le=10, description='Search depth'),
    yj=Depends(get_yo_jenkins),
):
    """Search for jobs matching a REGEX pattern."""
    results, urls = await run_in_threadpool(
        yj.job.search,
        search_pattern=pattern,
        folder_name=folder,
        folder_depth=depth,
    )
    return {'results': results, 'urls': urls}


@router.get('/info')
async def job_info(
    job: str = Query(..., description='Job name or URL'),
    yj=Depends(get_yo_jenkins),
):
    """Get job information."""
    from yojenkins.utility.utility import is_full_url

    if is_full_url(job):
        validate_jenkins_url(job, yj)
        return await run_in_threadpool(yj.job.info, job_url=job)
    return await run_in_threadpool(yj.job.info, job_name=job)


@router.post('/build')
async def trigger_build(
    job: str = Query(..., description='Job name or URL'),
    yj=Depends(get_yo_jenkins),
):
    """Trigger a build for the specified job."""
    from yojenkins.utility.utility import is_full_url

    if is_full_url(job):
        validate_jenkins_url(job, yj)
        queue_number = await run_in_threadpool(yj.job.build_trigger, job_url=job)
    else:
        queue_number = await run_in_threadpool(yj.job.build_trigger, job_name=job)
    return {'queue_number': queue_number}


@router.get('/builds')
async def job_builds(
    job: str = Query(..., description='Job name or URL'),
    yj=Depends(get_yo_jenkins),
):
    """List all builds for a job."""
    from yojenkins.utility.utility import is_full_url

    if is_full_url(job):
        validate_jenkins_url(job, yj)
        builds, urls = await run_in_threadpool(yj.job.build_list, job_url=job)
    else:
        builds, urls = await run_in_threadpool(yj.job.build_list, job_name=job)
    return {'builds': builds, 'urls': urls}
