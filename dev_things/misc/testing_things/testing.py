import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint
import json
from datetime import datetime, timedelta

# NOTE:
#   Job -> Build -> Stage -> Step

username = "USERNAME"
password = ""
jenkins_server_url = 'base_url'

# NOTE: make utility for requests, error checking and all

# Get Build information
job_url = f"{jenkins_server_url}/job/doggy/job/money-movement/job/mf-status-tracker/job/master/"
build_number = 16
request_url = f"{job_url}/{build_number}/wfapi/describe"
print(request_url)
request_return = requests.get(request_url, auth=HTTPBasicAuth(username, password))

if request_return.status_code == 404:
    print('404 ERROR')

try:
    build_return_content = request_return.json()
    pprint(build_return_content)
except Exception as e:
    print(f"Failed to parse request return. Possible HTML content. Exception: {e})")
    exit()

# pprint(build_return_content)
# input()

print('\n\n')

# Get stage information
for stage in build_return_content['stages']:
    print('\n')
    print(f'==================================================================')
    print(f'==================  STAGE: {stage["name"]}  ======================')
    print(f'==================================================================')

    request_url = f"{jenkins_server_url}/{stage['_links']['self']['href']}"
    print(request_url)
    request_return = requests.get(request_url, auth=HTTPBasicAuth(username, password))
    stage_return_content = request_return.json()
    if not stage_return_content:
        continue

    # pprint(stage)
    # input()

    # Get step information
    for step in stage_return_content['stageFlowNodes']:
        if 'parameterDescription' in step:
            print(f"[{step['status']}] - {step['name']} - {step['parameterDescription']}")
        else:
            print(f"[{step['status']}] - {step['name']} -  Jenkins Step")

        # pprint(step)
        # input()

    start_datetime = datetime.fromtimestamp(stage["startTimeMillis"] / 1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
    duration = str(timedelta(seconds=stage["durationMillis"] / 1000.0))

    # NOTE: Stage does not have 'endTimeMillis'

    print('-------------------------------------------')
    print(f'STAGE START:     {start_datetime}')
    print(f'STAGE DURATION:  {duration}')
    print(f'STAGE STATUS:    {stage["status"]}')
    print('-------------------------------------------')

    pprint(stage)
    input()

start_datetime = datetime.fromtimestamp(build_return_content["startTimeMillis"] /
                                        1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
end_datetime = datetime.fromtimestamp(build_return_content["endTimeMillis"] /
                                      1000.0).strftime("%A, %B %d, %Y %I:%M:%S")
duration = str(timedelta(seconds=build_return_content["durationMillis"] / 1000.0))

print('-------------------------------------------')
print(f'BUILD START:     {start_datetime}')
print(f'BUILD END:       {end_datetime}')
print(f'BUILD DURATION:  {duration}')
print(f'BUILD STATUS:    {build_return_content["status"]}')
print('-------------------------------------------')
