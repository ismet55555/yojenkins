"""FastAPI application factory."""

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from yojenkins import __version__
from yojenkins.api.auth import router as auth_router
from yojenkins.api.dependencies import cleanup_expired_sessions
from yojenkins.api.routers.builds import router as builds_router
from yojenkins.api.routers.folders import router as folders_router
from yojenkins.api.routers.jobs import router as jobs_router
from yojenkins.api.routers.server import router as server_router
from yojenkins.api.websocket import router as ws_router
from yojenkins.yo_jenkins.exceptions import (
    AuthenticationError,
    NotFoundError,
    RequestError,
    ValidationError,
    YoJenkinsException,
)


async def _session_cleanup_loop():
    """Periodically remove expired sessions."""
    while True:
        # 5 min between sweeps — frequent enough to bound memory from expired
        # sessions, infrequent enough to be negligible overhead.
        await asyncio.sleep(300)
        cleanup_expired_sessions()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: start session cleanup background task."""
    task = asyncio.create_task(_session_cleanup_loop())
    yield
    task.cancel()


def create_app(static_dir: Optional[str] = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title='yojenkins',
        description='Web API for managing Jenkins servers',
        version=__version__,
        lifespan=lifespan,
    )

    # Dev-mode CORS: localhost:3000 (CRA) and localhost:5173 (Vite).
    # In production the SPA is served from the same origin, so CORS is unused.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:3000', 'http://localhost:5173'],
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'DELETE'],
        allow_headers=['Content-Type', 'Authorization'],
    )

    @app.middleware('http')
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        return response

    # Register routers
    app.include_router(auth_router, prefix='/api/auth', tags=['auth'])
    app.include_router(server_router, prefix='/api/server', tags=['server'])
    app.include_router(jobs_router, prefix='/api/jobs', tags=['jobs'])
    app.include_router(builds_router, prefix='/api/builds', tags=['builds'])
    app.include_router(folders_router, prefix='/api/folders', tags=['folders'])
    app.include_router(ws_router, prefix='/api/ws', tags=['websocket'])

    # Exception handlers
    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(status_code=401, content={'detail': str(exc)})

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={'detail': str(exc)})

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        return JSONResponse(status_code=400, content={'detail': str(exc)})

    @app.exception_handler(RequestError)
    async def request_error_handler(request: Request, exc: RequestError):
        return JSONResponse(status_code=502, content={'detail': str(exc)})

    @app.exception_handler(YoJenkinsException)
    async def generic_handler(request: Request, exc: YoJenkinsException):
        return JSONResponse(status_code=500, content={'detail': str(exc)})

    # Serve built frontend static files (production mode)
    if static_dir:
        static_path = Path(static_dir).resolve()
        if static_path.is_dir() and (static_path / 'index.html').exists():

            @app.get('/{full_path:path}')
            async def serve_spa(full_path: str):
                """Serve static files or index.html for SPA routing."""
                file_path = (static_path / full_path).resolve()
                try:
                    file_path.relative_to(static_path)
                except ValueError:
                    return FileResponse(static_path / 'index.html')
                if full_path and file_path.is_file():
                    return FileResponse(file_path)
                return FileResponse(static_path / 'index.html')

    return app


# Module-level app instance for uvicorn: `uvicorn yojenkins.api.app:app`
app = create_app(static_dir=os.environ.get('YOJENKINS_STATIC_DIR'))
