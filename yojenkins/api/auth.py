"""JWT authentication endpoints."""

import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.concurrency import run_in_threadpool

from yojenkins.api.dependencies import create_access_token, get_yo_jenkins, store_session
from yojenkins.api.schemas import LoginRequest, LoginResponse, MessageResponse
from yojenkins.yo_jenkins.auth import Auth
from yojenkins.yo_jenkins.exceptions import YoJenkinsException
from yojenkins.yo_jenkins.rest import Rest
from yojenkins.yo_jenkins.yojenkins import YoJenkins

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate with a Jenkins server and receive a JWT."""
    # Demo mode bypass (requires YOJENKINS_DEMO_MODE env var)
    if request.username == "demo" and request.api_token == "demo":
        if not os.environ.get("YOJENKINS_DEMO_MODE"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Demo mode is not enabled. Set YOJENKINS_DEMO_MODE=1 to enable.",
            )
        from yojenkins.api.demo import DemoYoJenkins

        yj = DemoYoJenkins()
        user_id = str(uuid.uuid4())
        store_session(user_id, yj)
        token = create_access_token(user_id)
        return LoginResponse(access_token=token)

    auth = Auth(Rest())

    profile_info = {
        "jenkins_server_url": request.jenkins_url,
        "username": request.username,
        "api_token": request.api_token,
        "active": True,
        "profile": "web_session",  # Distinguishes web sessions from CLI profiles on disk
    }

    try:
        auth.jenkins_profile = profile_info
        await run_in_threadpool(auth.create_auth, profile_info=profile_info)
    except YoJenkinsException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    yj = YoJenkins(auth)
    user_id = str(uuid.uuid4())
    store_session(user_id, yj)
    token = create_access_token(user_id)

    return LoginResponse(access_token=token)


@router.get("/verify", response_model=MessageResponse)
async def verify(yj=Depends(get_yo_jenkins)):
    """Verify the current session is still valid."""
    try:
        result = await run_in_threadpool(yj.auth.verify)
        if result:
            return MessageResponse(message="Authenticated")
    except YoJenkinsException as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.get("/user")
async def user_info(yj=Depends(get_yo_jenkins)):
    """Get current user information."""
    try:
        return await run_in_threadpool(yj.auth.user)
    except YoJenkinsException as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
