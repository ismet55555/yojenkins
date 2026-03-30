"""Demo mode: duck-typed YoJenkins that returns fake data."""

import re

from yojenkins.api.demo import data


class DemoAuth:
    def verify(self):
        return True

    def user(self):
        return data.USER_INFO


class DemoRest:
    def request(self, url, method, *args):
        """Return demo console logs for any request."""
        return data.CONSOLE_LOG, {}, True


class DemoServer:
    def info(self):
        return data.SERVER_INFO

    def people(self):
        return data.PEOPLE, data.PEOPLE_LIST

    def queue_info(self):
        return data.QUEUE


class DemoJob:
    def search(self, search_pattern=".*", folder_name="", folder_depth=4):
        pattern = re.compile(search_pattern, re.IGNORECASE)
        matched = [j for j in data.JOBS if pattern.search(j["fullName"])]
        if folder_name:
            matched = [j for j in matched if j.get("folder", "") == folder_name]
        urls = [j["url"] for j in matched]
        return matched, urls

    def info(self, job_name=None, job_url=None):
        job = self._find(job_name, job_url)
        if job is None:
            return {}
        result = dict(job)
        builds = data.BUILDS.get(job["fullName"], [])
        result["builds"] = builds
        if builds:
            result["lastBuild"] = {"number": builds[0]["number"], "url": builds[0]["url"]}
        return result

    def build_trigger(self, job_name=None, job_url=None):
        return 42  # Arbitrary fake queue item ID for demo mode

    def build_list(self, job_name=None, job_url=None):
        job = self._find(job_name, job_url)
        if job is None:
            return [], []
        builds = data.BUILDS.get(job["fullName"], [])
        urls = [b["url"] for b in builds]
        return builds, urls

    def _find(self, job_name=None, job_url=None):
        for j in data.JOBS:
            if job_url and j["url"] == job_url.rstrip("/") + "/":
                return j
            if job_url and job_url.rstrip("/") == j["url"].rstrip("/"):
                return j
            if job_name and j["fullName"] == job_name:
                return j
            if job_name and j["name"] == job_name:
                return j
        return data.JOBS[0] if data.JOBS else None


class DemoBuild:
    def info(self, build_url=None):
        build = self._find(build_url)
        return build if build else {}

    def stage_list(self, build_url=None):
        build = self._find(build_url)
        if not build:
            return [], []
        result = build.get("result")
        if result == "FAILURE":
            return data.FAILURE_STAGES, data.FAILURE_STAGE_NAMES
        if result == "UNSTABLE":
            return data.UNSTABLE_STAGES, data.UNSTABLE_STAGE_NAMES
        return data.DEFAULT_STAGES, data.DEFAULT_STAGE_NAMES

    def _find(self, build_url=None):
        if not build_url:
            return None
        normalized = build_url.rstrip("/") + "/"
        for builds in data.BUILDS.values():
            for b in builds:
                if b["url"] == normalized or b["url"].rstrip("/") == build_url.rstrip("/"):
                    return b
        return None


class DemoFolder:
    def search(self, search_pattern=".*", folder_depth=4):
        pattern = re.compile(search_pattern, re.IGNORECASE)
        matched = [f for f in data.FOLDERS if pattern.search(f["name"])]
        urls = [f["url"] for f in matched]
        return matched, urls

    def info(self, folder_name=None, folder_url=None):
        folder = self._find(folder_name, folder_url)
        if folder is None:
            return {}
        result = dict(folder)
        result["jobs"] = [j for j in data.JOBS if j.get("folder") == folder["name"]]
        return result

    def jobs_list(self, folder_name=None, folder_url=None):
        folder = self._find(folder_name, folder_url)
        if folder is None:
            return [], []
        jobs = [j for j in data.JOBS if j.get("folder") == folder["name"]]
        urls = [j["url"] for j in jobs]
        return jobs, urls

    def _find(self, folder_name=None, folder_url=None):
        for f in data.FOLDERS:
            if folder_url and (f["url"] == folder_url.rstrip("/") + "/" or f["url"].rstrip("/") == folder_url.rstrip("/")):
                return f
            if folder_name and f["name"] == folder_name:
                return f
            if folder_name and f["fullName"] == folder_name:
                return f
        return None


class DemoYoJenkins:
    """Duck-typed stand-in for YoJenkins that returns demo data."""

    def __init__(self):
        self.auth = DemoAuth()
        self.rest = DemoRest()
        self.server = DemoServer()
        self.job = DemoJob()
        self.build = DemoBuild()
        self.folder = DemoFolder()
