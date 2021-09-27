import logging
from pprint import pprint

import coloredlogs
import jenkins

# Creating a message logger
format = f"[%(asctime)s][%(levelname)-10s] %(message)s"
logger = logging.basicConfig(level=logging.INFO, format=format, datefmt="%d-%b-%y %H:%M:%S")
logger = logging.getLogger()

# Applying color to the output logs
colored_logger = coloredlogs.install(fmt=format, datefmt=data_format, logger=logger)
logger.info('START')

###############################################################################
###############################################################################

# Connecting to Jenkins (Exception handling: jenkins.JenkinsException)
J = jenkins.Jenkins(url='https://localhost:8080/',
                    username='yoyo',
                    password='11e575255371c28c3f0b5482257e65a58f',
                    timeout=5)

# Getting user name
try:
    user = J.get_whoami()
except jenkins.JenkinsException as e:
    error_no_html = e.args[0].split("\n")[0]
    logger.fatal(f'Jenkins server authentication failed.')
    logger.fatal(f'Exception: {error_no_html}')
    logger.fatal(f'Possible causes:')
    logger.fatal(f'  - Wrong Jenkins server URL')
    logger.fatal(f'  - Incorrect credentials')
    logger.fatal(f'  - Expired API Token')
    logger.fatal('')
    logger.fatal('To update Jenkins credentials run:')
    logger.fatal('    yo-jenkins --configure')

# Getting Jenkins version
version = J.get_version()
print('Hello %s from Jenkins %s' % (user['fullName'], version))

job_name = 'doggy/Small-Business-Money-Movement/mf-status-tracker/doggy-migration-FROM-money-movement'
# job_name = 'doggy/job/Small-Business-Money-Movement/job/mf-status-tracker/job/doggy-migration-FROM-money-movement'
job_name = "https://localhost:8080/job/Non-PAR/job/Non-Prod-Jobs/job/Something/"
job_name = "doggy/cool/tools-out-of-wallet-sessions-api/master"

# # See if job exists (True or None)
# job_exists = J.job_exists(job_name)
# pprint(job_exists)

# get_jobs = J.get_jobs(job_name)
# pprint(get_jobs)

# # Get job info
# job_info = J.get_job_info(name=job_name)
# pprint(job_info)

# # Get debug info (human readable)
# job_debug = J.debug_job_info(job_name))
# pprint(job_debug)

# job_config = J.get_job_config(job_name)
# pprint(job_config)

# # Trigger a Job build  (Exception handling: jenkins.NotFoundException)
# out = J.build_job(job_name, parameters=None, token=None)
# pprint(out)

# # Getting the next build number
# next_bn = J.get_job_info(job_name)['nextBuildNumber']
# print(next_bn)

# # Updating the next build number
# out = J.set_next_build_number(job_name, next_bn + 1)
# print(out)

# Getting the last job run
last_build_number = J.get_job_info(job_name)['lastCompletedBuild']['number']
print(last_build_number)

# Getting the job info
build_info = J.get_build_info(job_name, last_build_number)
pprint(build_info)

# # Getting console output (output single string, with new line charcaters)
# out = J.get_build_console_output(job_name, last_build_number)
# # print(out)

# # Delete a build (Exception handling: jenkins.NotFoundException)
# out = J.delete_build(name=job_name, number=8)
# pprint(out)
