"""Tests for the FastAPI web API endpoints."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Enable demo mode for tests
os.environ["YOJENKINS_DEMO_MODE"] = "1"

from yojenkins.api.app import create_app
from yojenkins.api.dependencies import _sessions, cleanup_expired_sessions


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear session store between tests."""
    _sessions.clear()
    yield
    _sessions.clear()


@pytest.fixture
def client():
    """TestClient without static file serving."""
    app = create_app(static_dir=None)
    return TestClient(app)


@pytest.fixture
def demo_token(client):
    """Get a valid JWT by logging in with demo credentials."""
    resp = client.post("/api/auth/login", json={
        "jenkins_url": "http://demo",
        "username": "demo",
        "api_token": "demo",
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


# --- Authentication tests ---

class TestAuth:
    def test_demo_login_success(self, client):
        resp = client.post("/api/auth/login", json={
            "jenkins_url": "http://demo",
            "username": "demo",
            "api_token": "demo",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_demo_login_disabled(self, client):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("YOJENKINS_DEMO_MODE", None)
            resp = client.post("/api/auth/login", json={
                "jenkins_url": "http://demo",
                "username": "demo",
                "api_token": "demo",
            })
            assert resp.status_code == 403
            assert "Demo mode is not enabled" in resp.json()["detail"]
        # Restore for other tests
        os.environ["YOJENKINS_DEMO_MODE"] = "1"

    def test_unauthenticated_access(self, client):
        resp = client.get("/api/server/info")
        assert resp.status_code in (401, 403)  # Depends on FastAPI/HTTPBearer version

    def test_invalid_token(self, client):
        resp = client.get("/api/server/info", headers={
            "Authorization": "Bearer invalid.jwt.token"
        })
        assert resp.status_code == 401

    def test_verify_session(self, client, demo_token):
        resp = client.get("/api/auth/verify", headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200

    def test_user_info(self, client, demo_token):
        resp = client.get("/api/auth/user", headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200


# --- Server endpoints ---

class TestServer:
    def test_server_info(self, client, demo_token):
        resp = client.get("/api/server/info", headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200

    def test_server_people(self, client, demo_token):
        resp = client.get("/api/server/people", headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200


# --- Jobs endpoints ---

class TestJobs:
    def test_search_jobs(self, client, demo_token):
        resp = client.get("/api/jobs/search", params={"pattern": ".*"}, headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data

    def test_search_depth_bounds(self, client, demo_token):
        headers = {"Authorization": f"Bearer {demo_token}"}
        # depth too high
        resp = client.get("/api/jobs/search", params={"pattern": ".*", "depth": 99}, headers=headers)
        assert resp.status_code == 422
        # depth too low
        resp = client.get("/api/jobs/search", params={"pattern": ".*", "depth": 0}, headers=headers)
        assert resp.status_code == 422

    def test_search_pattern_too_long(self, client, demo_token):
        resp = client.get("/api/jobs/search", params={"pattern": "x" * 501}, headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 422

    def test_job_info(self, client, demo_token):
        resp = client.get("/api/jobs/info", params={"job": "backend-api"}, headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200

    def test_job_builds(self, client, demo_token):
        resp = client.get("/api/jobs/builds", params={"job": "backend-api"}, headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200


# --- Folders endpoints ---

class TestFolders:
    def test_search_folders(self, client, demo_token):
        resp = client.get("/api/folders/search", headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data

    def test_search_depth_bounds(self, client, demo_token):
        headers = {"Authorization": f"Bearer {demo_token}"}
        resp = client.get("/api/folders/search", params={"depth": 99}, headers=headers)
        assert resp.status_code == 422
        resp = client.get("/api/folders/search", params={"depth": 0}, headers=headers)
        assert resp.status_code == 422

    def test_folder_info(self, client, demo_token):
        resp = client.get("/api/folders/info", params={"folder": "DevOps"}, headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200

    def test_folder_jobs(self, client, demo_token):
        resp = client.get("/api/folders/jobs", params={"folder": "DevOps"}, headers={
            "Authorization": f"Bearer {demo_token}"
        })
        assert resp.status_code == 200


# --- Builds endpoints ---

class TestBuilds:
    def test_build_info(self, client, demo_token):
        resp = client.get("/api/builds/info", params={
            "url": "http://jenkins.example.com/job/backend-api/42/"
        }, headers={"Authorization": f"Bearer {demo_token}"})
        assert resp.status_code == 200

    def test_build_logs(self, client, demo_token):
        resp = client.get("/api/builds/logs", params={
            "url": "http://jenkins.example.com/job/backend-api/42/"
        }, headers={"Authorization": f"Bearer {demo_token}"})
        assert resp.status_code == 200


# --- Path traversal protection ---

class TestPathTraversal:
    def test_path_traversal_blocked(self):
        """Ensure ../../etc/passwd style paths are blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = Path(tmpdir) / "index.html"
            index.write_text("<html>OK</html>")
            app = create_app(static_dir=tmpdir)
            client = TestClient(app)

            resp = client.get("/../../etc/passwd")
            assert resp.status_code == 200
            assert "OK" in resp.text  # Returns index.html, not /etc/passwd

    def test_static_file_served(self):
        """Ensure legitimate static files are served."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = Path(tmpdir) / "index.html"
            index.write_text("<html>index</html>")
            assets_dir = Path(tmpdir) / "assets"
            assets_dir.mkdir()
            js_file = assets_dir / "app.js"
            js_file.write_text("console.log('hello')")

            app = create_app(static_dir=tmpdir)
            client = TestClient(app)

            resp = client.get("/assets/app.js")
            assert resp.status_code == 200
            assert "hello" in resp.text


# --- Security headers ---

class TestSecurityHeaders:
    def test_security_headers_present(self, client):
        resp = client.post("/api/auth/login", json={
            "jenkins_url": "http://demo",
            "username": "demo",
            "api_token": "demo",
        })
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"
        assert resp.headers.get("X-Frame-Options") == "DENY"


# --- Session cleanup ---

class TestSessionCleanup:
    def test_cleanup_removes_expired(self, client, demo_token):
        """Verify cleanup_expired_sessions removes stale sessions."""
        assert len(_sessions) == 1
        # Artificially age the session
        for uid in _sessions:
            yj, _ = _sessions[uid]
            _sessions[uid] = (yj, 0)  # Set last access to epoch
        cleanup_expired_sessions()
        assert len(_sessions) == 0

    def test_cleanup_keeps_fresh(self, client, demo_token):
        """Verify cleanup keeps recently-accessed sessions."""
        assert len(_sessions) == 1
        cleanup_expired_sessions()
        assert len(_sessions) == 1  # Still fresh
