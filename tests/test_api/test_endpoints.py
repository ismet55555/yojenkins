"""Tests for the FastAPI web API endpoints.

Mock strategy: Inject a MagicMock YoJenkins directly into the session store,
bypassing login entirely. This tests routes + dependency injection + response
serialization without requiring demo mode or a real Jenkins server.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from yojenkins.api.app import create_app
from yojenkins.api.dependencies import _sessions, cleanup_expired_sessions, create_access_token, store_session


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
def mock_yj():
    """MagicMock YoJenkins with plausible return values for all route handlers."""
    yj = MagicMock()
    yj.auth.verify.return_value = True
    yj.auth.user.return_value = {'id': 'test-user', 'fullName': 'Test User'}
    yj.server.info.return_value = {'mode': 'NORMAL', 'numExecutors': 2, 'url': 'http://test:8080'}
    yj.server.people.return_value = (
        {'users': [{'user': {'fullName': 'Alice'}}]},
        [{'fullName': 'Alice'}],
    )
    yj.server.queue_info.return_value = {'items': []}
    yj.job.search.return_value = (
        [{'name': 'backend-api', 'fullName': 'backend-api', 'url': 'http://test/job/backend-api/'}],
        ['http://test/job/backend-api/'],
    )
    yj.job.info.return_value = {'name': 'backend-api', 'url': 'http://test/job/backend-api/'}
    yj.job.build_list.return_value = (
        [{'number': 1, 'result': 'SUCCESS', 'url': 'http://test/job/backend-api/1/'}],
        ['http://test/job/backend-api/1/'],
    )
    yj.folder.search.return_value = (
        [{'name': 'DevOps', 'url': 'http://test/job/DevOps/'}],
        ['http://test/job/DevOps/'],
    )
    yj.folder.info.return_value = {'name': 'DevOps', 'url': 'http://test/job/DevOps/'}
    yj.folder.jobs_list.return_value = (
        [{'name': 'deploy', 'url': 'http://test/job/DevOps/job/deploy/'}],
        ['http://test/job/DevOps/job/deploy/'],
    )
    yj.build.info.return_value = {'number': 42, 'result': 'SUCCESS', 'url': 'http://test/job/backend-api/42/'}
    yj.build.stage_list.return_value = (
        [{'name': 'Build', 'status': 'SUCCESS'}],
        ['Build'],
    )
    yj.rest.request.return_value = ('Started: build #42\nFinished: SUCCESS', {}, True)
    yj.rest.server_url = 'http://test:8080/'
    return yj


@pytest.fixture
def auth_token(mock_yj):
    """Inject mock YoJenkins into session store and return a valid JWT."""
    user_id = 'test-user-id'
    store_session(user_id, mock_yj)
    return create_access_token(user_id)


# --- Authentication tests ---


class TestAuth:
    def test_unauthenticated_access(self, client):
        resp = client.get('/api/server/info')
        assert resp.status_code in (401, 403)

    def test_invalid_token(self, client):
        resp = client.get('/api/server/info', headers={'Authorization': 'Bearer invalid.jwt.token'})
        assert resp.status_code == 401

    def test_verify_session(self, client, auth_token):
        resp = client.get('/api/auth/verify', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 200

    def test_user_info(self, client, auth_token):
        resp = client.get('/api/auth/user', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 200


# --- Server endpoints ---


class TestServer:
    def test_server_info(self, client, auth_token):
        resp = client.get('/api/server/info', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 200

    def test_server_people(self, client, auth_token):
        resp = client.get('/api/server/people', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 200


# --- Jobs endpoints ---


class TestJobs:
    def test_search_jobs(self, client, auth_token):
        resp = client.get(
            '/api/jobs/search', params={'pattern': '.*'}, headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert 'results' in data

    def test_search_depth_bounds(self, client, auth_token):
        headers = {'Authorization': f'Bearer {auth_token}'}
        # depth too high
        resp = client.get('/api/jobs/search', params={'pattern': '.*', 'depth': 99}, headers=headers)
        assert resp.status_code == 422
        # depth too low
        resp = client.get('/api/jobs/search', params={'pattern': '.*', 'depth': 0}, headers=headers)
        assert resp.status_code == 422

    def test_search_pattern_too_long(self, client, auth_token):
        resp = client.get(
            '/api/jobs/search', params={'pattern': 'x' * 501}, headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert resp.status_code == 422

    def test_job_info(self, client, auth_token):
        resp = client.get(
            '/api/jobs/info', params={'job': 'backend-api'}, headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert resp.status_code == 200

    def test_job_builds(self, client, auth_token):
        resp = client.get(
            '/api/jobs/builds', params={'job': 'backend-api'}, headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert resp.status_code == 200


# --- Folders endpoints ---


class TestFolders:
    def test_search_folders(self, client, auth_token):
        resp = client.get('/api/folders/search', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert 'results' in data

    def test_search_depth_bounds(self, client, auth_token):
        headers = {'Authorization': f'Bearer {auth_token}'}
        resp = client.get('/api/folders/search', params={'depth': 99}, headers=headers)
        assert resp.status_code == 422
        resp = client.get('/api/folders/search', params={'depth': 0}, headers=headers)
        assert resp.status_code == 422

    def test_folder_info(self, client, auth_token):
        resp = client.get(
            '/api/folders/info', params={'folder': 'DevOps'}, headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert resp.status_code == 200

    def test_folder_jobs(self, client, auth_token):
        resp = client.get(
            '/api/folders/jobs', params={'folder': 'DevOps'}, headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert resp.status_code == 200


# --- Builds endpoints ---


class TestBuilds:
    def test_build_info(self, client, auth_token):
        resp = client.get(
            '/api/builds/info',
            params={'url': 'http://test:8080/job/backend-api/42/'},
            headers={'Authorization': f'Bearer {auth_token}'},
        )
        assert resp.status_code == 200

    def test_build_logs(self, client, auth_token):
        resp = client.get(
            '/api/builds/logs',
            params={'url': 'http://test:8080/job/backend-api/42/'},
            headers={'Authorization': f'Bearer {auth_token}'},
        )
        assert resp.status_code == 200


# --- Path traversal protection ---


class TestPathTraversal:
    def test_path_traversal_blocked(self):
        """Ensure ../../etc/passwd style paths are blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = Path(tmpdir) / 'index.html'
            index.write_text('<html>OK</html>')
            app = create_app(static_dir=tmpdir)
            client = TestClient(app)

            resp = client.get('/../../etc/passwd')
            assert resp.status_code == 200
            assert 'OK' in resp.text  # Returns index.html, not /etc/passwd

    def test_static_file_served(self):
        """Ensure legitimate static files are served."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index = Path(tmpdir) / 'index.html'
            index.write_text('<html>index</html>')
            assets_dir = Path(tmpdir) / 'assets'
            assets_dir.mkdir()
            js_file = assets_dir / 'app.js'
            js_file.write_text("console.log('hello')")

            app = create_app(static_dir=tmpdir)
            client = TestClient(app)

            resp = client.get('/assets/app.js')
            assert resp.status_code == 200
            assert 'hello' in resp.text


# --- Security headers ---


class TestSecurityHeaders:
    def test_security_headers_present(self, client, auth_token):
        resp = client.get('/api/auth/verify', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.headers.get('X-Content-Type-Options') == 'nosniff'
        assert resp.headers.get('X-Frame-Options') == 'DENY'


# --- Session cleanup ---


class TestSessionCleanup:
    def test_cleanup_removes_expired(self, client, auth_token):
        """Verify cleanup_expired_sessions removes stale sessions."""
        assert len(_sessions) == 1
        # Artificially age the session
        for uid in _sessions:
            yj, _ = _sessions[uid]
            _sessions[uid] = (yj, 0)  # Set last access to epoch
        cleanup_expired_sessions()
        assert len(_sessions) == 0

    def test_cleanup_keeps_fresh(self, client, auth_token):
        """Verify cleanup keeps recently-accessed sessions."""
        assert len(_sessions) == 1
        cleanup_expired_sessions()
        assert len(_sessions) == 1  # Still fresh
