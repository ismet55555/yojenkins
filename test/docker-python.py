#!/usr/bin/env python3

from pprint import pprint
from time import time
import docker
import sys
import os
import logging

# Setup a message logging
log_format = '[%(asctime)s] [%(relativeCreated)-4d] [%(filename)-23s:%(lineno)4s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format, datefmt='%H:%M:%S')




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
# Check if existing container is already running
container_name = 'jenkins'
try:
    exiting_container = client.containers.get(container_name)
    logging.warning('Existing container found with same tag. Killing existing container ...')
    exiting_container.kill()
    logging.warning('Existing container is now dead')
except:
    pass



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
logging.info(f'Successfully build image (Elapsed time: {time() - start_time}s)')

# Get the image tag
image_tag = image[0].tags[0]




##############################################################################
#                            CREATE VOLUME
##############################################################################
logging.info('===> CREATING VOLUME MOUNTS ...')

mounts = []

# Bind Volume Mounts
volume_bind = {}
if volume_bind:
    for volume_source, volume_target in volume_bind.items():
        logging.info(f'Adding to list local bind volume mount: {volume_source} -> {volume_target} ...')
        mount = docker.types.Mount(
            source=volume_source,
            target=volume_target,
            type='bind',
            read_only=False
        )
        mounts.append(mount)

# Named Volume
new_volume = True
volume_named = {'jenkins': '/var/jenkins_home'}
for volume_name, volume_dir in volume_named.items():
    try:
        volume_named = client.volumes.get(volume_name)

        if new_volume:
            logging.info(f'Removing found matching/existing named volume: {volume_name} ...')
            volume_named.remove(force=True)
        else:
            logging.warning(f'Using found matching/existing named volume: {volume_name}')

    except:
        logging.info(f'Creating new named volume: {volume_name}')
        volume_named = client.volumes.create(
            name=volume_name,
            driver='local'
        )
        logging.info('Successfully created!')

    logging.info(f'Adding to list named volume mount: {volume_name} ...')
    mount = docker.types.Mount(
        target=volume_dir,
        source=volume_name,
        type='volume',
        read_only=False
    )
    mounts.append(mount)

logging.info(f'Number of volumes to be mounted: {len(mounts)}')




##############################################################################
#                             RUN CONTAINER
##############################################################################
logging.info('===> RUNNING THE CONTAINER ...')
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

# Running the container
logging.info(f'Creating and running container: {container_name} ...')
container = client.containers.run(
    name=container_name,
    image=image_tag,
    environment=env_vars,
    ports=ports,
    mounts=mounts,
    remove=True,
    auto_remove=True,
    detach=True
    )
logging.info(f'Container "{container_name}" is running on local port {list(ports.values())[0]}!')



logging.info('DONE')
