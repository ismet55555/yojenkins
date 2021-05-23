#!/usr/bin/env python3


from pprint import pprint
from time import time
import docker
import sys
import os
import logging

# Setup a message logging
log_format = '[%(asctime)s] [%(relativeCreated)-4d] [%(filename)-23s:%(lineno)4s] %(message)s'
logging.basicConfig(level=logging.INFO,
                    format=log_format,
                    datefmt='%H:%M:%S'
                    )



##############################################################################
#                                   SETUP
##############################################################################
# Get the local docker client
client = docker.from_env()

# Ping the docker client
if not client.ping():
    logging.info('ERROR: Cannot reach docker client')
    sys.exit(1)



##############################################################################
#                              BUILD IMAGE
##############################################################################
logging.info('===> BUILDING DOCKER IMAGE ...')
start_time = time()
dockerfile_dir = os.path.join(os.getcwd(), 'misc/jenkins-container')
logging.info(f'DOCKERFILE DIRECTORY: {dockerfile_dir}')
image = client.images.build(
    path=dockerfile_dir,
    tag='jenkins:jcasc',
    rm=True,
    quiet=False
)
logging.info(f'Successfully build image (Elapsed time: {time() - start_time})')

# Get the image tag
image_tag = image[0].tags[0]



##############################################################################
#                             RUN CONTAINER
##############################################################################
logging.info('===> RUNNING THE CONTAINER ...')
name = 'jenkins'
env_vars = [
    'JENKINS_ADMIN_ID=admin',
    'JENKINS_ADMIN_PASSWORD=password'
]
ports = {
    '8080/tcp': 8080,
    '50000/tcp': 50000
}
restart_policy={
    "Name": "on-failure",
    "MaximumRetryCount": 5
    }
bind_volume = {
    '~/jenkins:/var/jenkins_home'
}


volumes = {
f'{os.getcwd()}': {
    'bind': '/var/jenkins_home',
    'mode': 'rw'
    }
}


# Check if existing container is already running
try:
    exiting_container = client.containers.get(name)
    logging.warning('Existing container found with same tag. Killing existing container ...')
    exiting_container.kill()
    logging.warning('Existing container dead')
except:
    pass

# Running the container
container = client.containers.run(
    name=name,
    image=image_tag,
    environment=env_vars,
    ports=ports,
    volumes=volumes,
    remove=True,
    auto_remove=True,
    detach=True
    )
logging.info(f'Container "{name}" is running on local port: {list(ports.values())[0]}!')



logging.info('DONE')
