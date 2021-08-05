# Node/Agent Creation with Docker

## Goal
1. Setup a ephemeral node/agent (Only started once job is run, Docker based)
   1. Locally - Same architecture as host
   2. Remotely - Public IP address or DNS reference

2. Setup a persistent node/agent - Can we do this?
   1. Locally - Through an created docker container (created with yo-jenkins or independently)
   2. Remotely - Public IP address or DNS reference

3. Ability to prepare/setup an existing remote host via SSH
   1. Install and configure docker


## Usage

```
yo-jenkins node node-deploy 3.23.24.154  <--- can be "local"
  --name agent1
  --labels linux,test
  --image my_repo/my_image:latest         <--- default image "jenkins/ssh-agent:alpine"
  --jenkins-home /home/jenkins
  --user root                             <--- If a custom image is used
  --public-key ~/.ssh/mykey               <--- (SSH credentials or location of private key)
  --persist                               <--- Persist the agent, deploys and forgets
```


---

## Manual Setup Process for Persistent Node

1. Independently, setup host
   1. Add `jenkins` user: `sudo adduser jenkins --shell /bin/bash`
   2. Log in as `jenkins` user: `su jenkins`
   3. Install and configure Docker
   4. Add public key to `~/.ssh/authorized_keys`
   5. Setup and start SSHD service
   6. Install Java
   7. If using Docker: `docker run --name jenkins-ssh-agent jenkins/ssh-agent $JENKINS_AGENT_SSH_PUBKEY`

2. Manage Jenkins > Manage Nodes and Clouds > Add Node
   1. Permanent Node
   2. Remote Root Directory: `/home/jenkins`
   3. Launch agents with SSH
      1. Host: Host of host or docker container
      2. Credentials: Add private key in Jenkins credentials, User: Jenkins
      3. No host key verification startegy
      4. Advanced -> Java Path: Path to host's java binary (ie. `/usr/local/openjdk-8/bin/java`)


## Manual Setup Process for Ephemeral Node

1. Manage Jenkins > Manage Nodes and Clouds > Configure Clouds

2. Docker Cloud Details
   - Docker Host URI: unix:///var/run/docker.sock
   - Enabled
   - Advanced > Docker Hostname or IP address: 172.17.0.1 (Host IP for Docker Gateway)
   - Test Connection

3. Docker Agent Templates...
   - Docker Image: jenkins/ssh-agent
     - Must have SSHD running
     - Must have Java installed
   - Connect with SSH
     - Inject SSH Key
       - User: `jenkins`
       - Advanced > JavaPath: `/usr/local/openjdk-8/bin/java`
     - Use configured SSH Credentials (DID NOT WORK)
       - SSH Credentials: Private key is stored in Jenkins credentials
       - Host Key Verification Strategy: Known hosts file Verification Strategy
   - Node Properties
     - Environment Variables: `JENKINS_AGENT_SSH_PUBKEY`: `[YOUR PUBLIC KEY]`


---

## Challenges

- Passing group ID to docker container 
  - This is a docker-in-docker problem
  - Currently using Python Docker SDK at container run (group_add=[docker_gid])
    - How does this work on Windows and setting up a remote windows host?
    - Remote host will not be using the same docker engine
    - Only containers on the same host will need this

- Windows agents


## Next Steps

1. Set up remote agent on AWS EC2 via SSH
2. 

---

## Random

- Programmatically, Use same class as the server?
  - Start a new class then see later if we can combine to a base class somehow
  
- Configuration as code
  - Either prepackaged image or custom Dockerfile
  - If remote, this needs to be available on Dockerhub
  - If remote, maybe we can send via SSH? JNLP? Too large?

- Linux vs Windows option
  - Is it even possible to host a windows container on linux or macos? - NO
  - Can only deploy windows node if base OS is windows and docker is windows-based

- Maybe have a remote server setup script ready to go that preps it
  - Docker settings, restarts services, etc ...
  - yo-jenkins node prep 13.54.56.34 ec2-user
        --ssh-password password
        --ssh-private-key path_to_key

- Condigure Cloud - Docker
  - Connect with JNLP 
  - Attach Docker container 
    - https://www.bogotobogo.com/DevOps/Docker/Docker-Jenkins-Master-Slave-Agent-ssh.php
    - Image Used: jenkins/inbound-agent

---

## Resources

- SSH Agent Image
  - https://hub.docker.com/r/jenkins/ssh-agent

- Dockerfile / Group ID passing
  - https://mikemybytes.com/2018/01/21/build-docker-images-with-jenkins-running-in-docker/

- Docker Plugin
  - https://kb.novaordis.com/index.php/Jenkins_Docker_Plugin

- How to
  - https://medium.com/xebia-engineering/using-docker-containers-as-jenkins-build-slaves-a0bb1c9190d
  - https://devopscube.com/docker-containers-as-build-slaves-jenkins/ 
  - https://youtu.be/3GAzfOk7XO8

- SSH Verfication Startegy
  - https://github.com/jenkinsci/ssh-slaves-plugin/blob/master/doc/CONFIGURE.md#host-key-verification-strategy

- Helpful Linux commands
  - Container IP: `sudo docker inspect -f "{{ .NetworkSettings.IPAddress }}" <CONTAINER>`
  - Java location: `which java`
  - All users: `awk -F: '{ print $1}' /etc/passwd`

