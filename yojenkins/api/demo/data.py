"""Static fake data for demo mode."""

BASE_URL = "http://demo-jenkins:8080"

# --- Server ---

SERVER_INFO = {
    "_class": "hudson.model.Hudson",
    "mode": "NORMAL",
    "nodeDescription": "the master Jenkins node",
    "nodeName": "",
    "numExecutors": 4,
    "description": "YoJenkins Demo Server",
    "quietingDown": False,
    "slaveAgentPort": 50000,
    "useCrumbIssuer": True,
    "useSecurity": True,
    "url": f"{BASE_URL}/",
    "version": "2.426.1",
}

PEOPLE = [
    {"fullName": "Alice Chen", "lastChange": 1711900000000, "project": "deploy-service"},
    {"fullName": "Bob Martinez", "lastChange": 1711890000000, "project": "api-gateway"},
    {"fullName": "Carol Wu", "lastChange": 1711880000000, "project": "frontend-app"},
    {"fullName": "Dan Okafor", "lastChange": 1711870000000, "project": "data-pipeline"},
    {"fullName": "Eve Patel", "lastChange": 1711860000000, "project": "auth-service"},
]

PEOPLE_LIST = [p["fullName"] for p in PEOPLE]

QUEUE = {
    "_class": "hudson.model.Queue",
    "discoverableItems": [],
    "items": [
        {
            "_class": "hudson.model.Queue$BuildableItem",
            "id": 101,
            "task": {
                "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
                "name": "data-pipeline",
                "url": f"{BASE_URL}/job/Backend/job/data-pipeline/",
            },
            "why": "Waiting for next available executor",
            "inQueueSince": 1711900000000,
            "buildableStartMilliseconds": 1711900001000,
            "stuck": False,
        },
    ],
}

# --- User ---

USER_INFO = {
    "_class": "hudson.security.HudsonPrivateSecurityRealm$Details",
    "fullName": "Demo User",
    "id": "demo",
    "absoluteUrl": f"{BASE_URL}/user/demo",
    "description": "Demo account for exploring yojenkins",
}

# --- Folders ---

FOLDERS = [
    {
        "_class": "com.cloudbees.hudson.plugins.folder.Folder",
        "name": "DevOps",
        "fullName": "DevOps",
        "url": f"{BASE_URL}/job/DevOps/",
        "description": "Infrastructure and deployment jobs",
    },
    {
        "_class": "com.cloudbees.hudson.plugins.folder.Folder",
        "name": "Backend",
        "fullName": "Backend",
        "url": f"{BASE_URL}/job/Backend/",
        "description": "Backend services and APIs",
    },
    {
        "_class": "com.cloudbees.hudson.plugins.folder.Folder",
        "name": "Frontend",
        "fullName": "Frontend",
        "url": f"{BASE_URL}/job/Frontend/",
        "description": "Frontend applications",
    },
]

FOLDER_URLS = [f["url"] for f in FOLDERS]

# --- Jobs ---
# Jenkins "color" encodes build status: blue=success, red=failed,
# yellow=unstable, notbuilt=never built. *_anime suffix=currently building.

JOBS = [
    {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "name": "deploy-service",
        "fullName": "DevOps/deploy-service",
        "url": f"{BASE_URL}/job/DevOps/job/deploy-service/",
        "color": "blue",
        "buildable": True,
        "nextBuildNumber": 85,
        "healthReport": [{"description": "Build stability: No recent builds failed.", "score": 100}],
        "folder": "DevOps",
    },
    {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "name": "infra-provisioning",
        "fullName": "DevOps/infra-provisioning",
        "url": f"{BASE_URL}/job/DevOps/job/infra-provisioning/",
        "color": "red",
        "buildable": True,
        "nextBuildNumber": 42,
        "healthReport": [{"description": "Build stability: 2 out of the last 5 builds failed.", "score": 60}],
        "folder": "DevOps",
    },
    {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "name": "api-gateway",
        "fullName": "Backend/api-gateway",
        "url": f"{BASE_URL}/job/Backend/job/api-gateway/",
        "color": "blue",
        "buildable": True,
        "nextBuildNumber": 128,
        "healthReport": [{"description": "Build stability: No recent builds failed.", "score": 100}],
        "folder": "Backend",
    },
    {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "name": "data-pipeline",
        "fullName": "Backend/data-pipeline",
        "url": f"{BASE_URL}/job/Backend/job/data-pipeline/",
        "color": "yellow",
        "buildable": True,
        "nextBuildNumber": 67,
        "healthReport": [{"description": "Build stability: 1 out of the last 5 builds failed.", "score": 80}],
        "folder": "Backend",
    },
    {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "name": "auth-service",
        "fullName": "Backend/auth-service",
        "url": f"{BASE_URL}/job/Backend/job/auth-service/",
        "color": "blue",
        "buildable": True,
        "nextBuildNumber": 93,
        "healthReport": [{"description": "Build stability: No recent builds failed.", "score": 100}],
        "folder": "Backend",
    },
    {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "name": "user-service",
        "fullName": "Backend/user-service",
        "url": f"{BASE_URL}/job/Backend/job/user-service/",
        "color": "blue_anime",
        "buildable": True,
        "nextBuildNumber": 55,
        "healthReport": [{"description": "Build stability: No recent builds failed.", "score": 100}],
        "folder": "Backend",
    },
    {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "name": "frontend-app",
        "fullName": "Frontend/frontend-app",
        "url": f"{BASE_URL}/job/Frontend/job/frontend-app/",
        "color": "blue",
        "buildable": True,
        "nextBuildNumber": 210,
        "healthReport": [{"description": "Build stability: No recent builds failed.", "score": 100}],
        "folder": "Frontend",
    },
    {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "name": "component-library",
        "fullName": "Frontend/component-library",
        "url": f"{BASE_URL}/job/Frontend/job/component-library/",
        "color": "notbuilt",
        "buildable": True,
        "nextBuildNumber": 1,
        "healthReport": [],
        "folder": "Frontend",
    },
    {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "name": "e2e-tests",
        "fullName": "Frontend/e2e-tests",
        "url": f"{BASE_URL}/job/Frontend/job/e2e-tests/",
        "color": "red",
        "buildable": True,
        "nextBuildNumber": 38,
        "healthReport": [{"description": "Build stability: 3 out of the last 5 builds failed.", "score": 40}],
        "folder": "Frontend",
    },
]

JOB_URLS = [j["url"] for j in JOBS]

# --- Builds ---

# keyed by job fullName
BUILDS: dict[str, list[dict]] = {
    "DevOps/deploy-service": [
        {"number": 84, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 95000, "durationFormatted": "1:35", "timestamp": 1711900000000, "startDatetime": "2024-03-31 18:26:40", "url": f"{BASE_URL}/job/DevOps/job/deploy-service/84/"},
        {"number": 83, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 87000, "durationFormatted": "1:27", "timestamp": 1711880000000, "startDatetime": "2024-03-31 12:53:20", "url": f"{BASE_URL}/job/DevOps/job/deploy-service/83/"},
        {"number": 82, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 102000, "durationFormatted": "1:42", "timestamp": 1711860000000, "startDatetime": "2024-03-31 07:20:00", "url": f"{BASE_URL}/job/DevOps/job/deploy-service/82/"},
    ],
    "DevOps/infra-provisioning": [
        {"number": 41, "result": "FAILURE", "resultText": "FAILURE", "duration": 45000, "durationFormatted": "0:45", "timestamp": 1711895000000, "startDatetime": "2024-03-31 17:03:20", "url": f"{BASE_URL}/job/DevOps/job/infra-provisioning/41/"},
        {"number": 40, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 180000, "durationFormatted": "3:00", "timestamp": 1711870000000, "startDatetime": "2024-03-31 10:06:40", "url": f"{BASE_URL}/job/DevOps/job/infra-provisioning/40/"},
        {"number": 39, "result": "FAILURE", "resultText": "FAILURE", "duration": 30000, "durationFormatted": "0:30", "timestamp": 1711850000000, "startDatetime": "2024-03-31 04:33:20", "url": f"{BASE_URL}/job/DevOps/job/infra-provisioning/39/"},
    ],
    "Backend/api-gateway": [
        {"number": 127, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 120000, "durationFormatted": "2:00", "timestamp": 1711898000000, "startDatetime": "2024-03-31 17:53:20", "url": f"{BASE_URL}/job/Backend/job/api-gateway/127/"},
        {"number": 126, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 115000, "durationFormatted": "1:55", "timestamp": 1711875000000, "startDatetime": "2024-03-31 11:30:00", "url": f"{BASE_URL}/job/Backend/job/api-gateway/126/"},
        {"number": 125, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 118000, "durationFormatted": "1:58", "timestamp": 1711855000000, "startDatetime": "2024-03-31 05:56:40", "url": f"{BASE_URL}/job/Backend/job/api-gateway/125/"},
    ],
    "Backend/data-pipeline": [
        {"number": 66, "result": "UNSTABLE", "resultText": "UNSTABLE", "duration": 240000, "durationFormatted": "4:00", "timestamp": 1711893000000, "startDatetime": "2024-03-31 16:30:00", "url": f"{BASE_URL}/job/Backend/job/data-pipeline/66/"},
        {"number": 65, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 210000, "durationFormatted": "3:30", "timestamp": 1711865000000, "startDatetime": "2024-03-31 08:43:20", "url": f"{BASE_URL}/job/Backend/job/data-pipeline/65/"},
    ],
    "Backend/auth-service": [
        {"number": 92, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 75000, "durationFormatted": "1:15", "timestamp": 1711899000000, "startDatetime": "2024-03-31 18:10:00", "url": f"{BASE_URL}/job/Backend/job/auth-service/92/"},
        {"number": 91, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 80000, "durationFormatted": "1:20", "timestamp": 1711878000000, "startDatetime": "2024-03-31 12:20:00", "url": f"{BASE_URL}/job/Backend/job/auth-service/91/"},
    ],
    "Backend/user-service": [
        {"number": 54, "result": None, "resultText": "RUNNING", "duration": 0, "durationFormatted": "0:00", "timestamp": 1711901000000, "startDatetime": "2024-03-31 18:43:20", "url": f"{BASE_URL}/job/Backend/job/user-service/54/"},
        {"number": 53, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 90000, "durationFormatted": "1:30", "timestamp": 1711882000000, "startDatetime": "2024-03-31 13:26:40", "url": f"{BASE_URL}/job/Backend/job/user-service/53/"},
    ],
    "Frontend/frontend-app": [
        {"number": 209, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 150000, "durationFormatted": "2:30", "timestamp": 1711897000000, "startDatetime": "2024-03-31 17:36:40", "url": f"{BASE_URL}/job/Frontend/job/frontend-app/209/"},
        {"number": 208, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 145000, "durationFormatted": "2:25", "timestamp": 1711876000000, "startDatetime": "2024-03-31 11:46:40", "url": f"{BASE_URL}/job/Frontend/job/frontend-app/208/"},
        {"number": 207, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 155000, "durationFormatted": "2:35", "timestamp": 1711856000000, "startDatetime": "2024-03-31 06:13:20", "url": f"{BASE_URL}/job/Frontend/job/frontend-app/207/"},
    ],
    "Frontend/e2e-tests": [
        {"number": 37, "result": "FAILURE", "resultText": "FAILURE", "duration": 300000, "durationFormatted": "5:00", "timestamp": 1711896000000, "startDatetime": "2024-03-31 17:20:00", "url": f"{BASE_URL}/job/Frontend/job/e2e-tests/37/"},
        {"number": 36, "result": "FAILURE", "resultText": "FAILURE", "duration": 285000, "durationFormatted": "4:45", "timestamp": 1711874000000, "startDatetime": "2024-03-31 11:13:20", "url": f"{BASE_URL}/job/Frontend/job/e2e-tests/36/"},
        {"number": 35, "result": "SUCCESS", "resultText": "SUCCESS", "duration": 310000, "durationFormatted": "5:10", "timestamp": 1711854000000, "startDatetime": "2024-03-31 05:40:00", "url": f"{BASE_URL}/job/Frontend/job/e2e-tests/35/"},
    ],
}

# Pipeline stage statuses per Jenkins Pipeline REST API:
# SUCCESS, FAILED, UNSTABLE, IN_PROGRESS.
DEFAULT_STAGES = [
    {"name": "Checkout", "status": "SUCCESS", "durationMillis": 5000, "id": "1"},
    {"name": "Build", "status": "SUCCESS", "durationMillis": 45000, "id": "2"},
    {"name": "Test", "status": "SUCCESS", "durationMillis": 30000, "id": "3"},
    {"name": "Deploy", "status": "SUCCESS", "durationMillis": 15000, "id": "4"},
]

FAILURE_STAGES = [
    {"name": "Checkout", "status": "SUCCESS", "durationMillis": 4800, "id": "1"},
    {"name": "Build", "status": "SUCCESS", "durationMillis": 42000, "id": "2"},
    {"name": "Test", "status": "FAILED", "durationMillis": 18000, "id": "3"},
]

UNSTABLE_STAGES = [
    {"name": "Checkout", "status": "SUCCESS", "durationMillis": 5200, "id": "1"},
    {"name": "Build", "status": "SUCCESS", "durationMillis": 50000, "id": "2"},
    {"name": "Test", "status": "UNSTABLE", "durationMillis": 35000, "id": "3"},
    {"name": "Deploy", "status": "SUCCESS", "durationMillis": 12000, "id": "4"},
]

DEFAULT_STAGE_NAMES = ["Checkout", "Build", "Test", "Deploy"]
FAILURE_STAGE_NAMES = ["Checkout", "Build", "Test"]
UNSTABLE_STAGE_NAMES = ["Checkout", "Build", "Test", "Deploy"]

# --- Console Logs ---

CONSOLE_LOG = """\
Started by user Demo User
Running in Durability level: MAX_SURVIVABILITY
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /var/jenkins_home/workspace/demo-job
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Checkout)
[Pipeline] checkout scm
Cloning the remote Git repository
Cloning repository https://github.com/example/demo-project.git
 > git init /var/jenkins_home/workspace/demo-job
 > git fetch --tags --force --progress -- https://github.com/example/demo-project.git +refs/heads/*:refs/remotes/origin/*
 > git checkout -f abc1234def5678
Commit message: "feat: add user dashboard component"
[Pipeline] }
[Pipeline] stage
[Pipeline] { (Build)
[Pipeline] sh
+ npm ci
added 1247 packages in 18.432s
+ npm run build
> demo-project@2.1.0 build
> vite build
vite v5.1.0 building for production...
✓ 342 modules transformed.
dist/index.html                  0.46 kB │ gzip:  0.30 kB
dist/assets/index-BkH5s21a.css   4.82 kB │ gzip:  1.52 kB
dist/assets/index-Ck3fE92b.js  186.42 kB │ gzip: 59.31 kB
✓ built in 1847ms
[Pipeline] }
[Pipeline] stage
[Pipeline] { (Test)
[Pipeline] sh
+ npm test

 PASS  src/components/Dashboard.test.tsx
 PASS  src/components/Header.test.tsx
 PASS  src/utils/api.test.ts
 PASS  src/hooks/useAuth.test.ts

Test Suites: 4 passed, 4 total
Tests:       23 passed, 23 total
Snapshots:   0 total
Time:        8.234s
[Pipeline] }
[Pipeline] stage
[Pipeline] { (Deploy)
[Pipeline] sh
+ kubectl apply -f k8s/deployment.yaml
deployment.apps/demo-project configured
service/demo-project unchanged
+ kubectl rollout status deployment/demo-project --timeout=120s
Waiting for deployment "demo-project" rollout to finish: 1 old replicas are pending termination...
deployment "demo-project" successfully rolled out
[Pipeline] }
[Pipeline] }
[Pipeline] End of Pipeline
Finished: SUCCESS
"""
