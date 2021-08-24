import json
from pprint import pprint
from string import Template

domain = 'http://localhost:8000/'
username = 'admin'
password = 'password'
description = 'This is a test'

# CRED_USER_PASS = {
#             "credentials": {
#                 "scope": f"{domain}",
#                 "username": f"{username}",
#                 "usernameSecret": False,
#                 "password": f"{password}",
#                 "description": f"{description}",
#                 "stapler-class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl",
#             }
#         }
# pprint(json.dumps(CRED_USER_PASS))



CRED_USER_PASS = '''{
    "credentials": {
        "scope": "${domain}",
        "username": "${username}",
        "usernameSecret": false,
        "password": "${password}",
        "description": "${description}",
        "stapler-class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl"
    }
}'''
t = Template(CRED_USER_PASS)
out = t.substitute(domain = 'http://localhost:8000/',
            username = 'admin',
            password = 'password',
            description = 'This is a test')
out_json = json.loads(out)
pprint(out_json)

# Do we need to convert to dict... only for debugging?
