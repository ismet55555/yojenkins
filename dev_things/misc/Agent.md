# Node/Agent Creation with Docker

## Goal

1. Setup a permanent node/agent
   1. Locally - Through an created docker container (created with yo-jenkins or independently)
   2. Remotely - Public IP address or DNS reference

2. Setup a ephemeral node/agent (Only started once job is run, Docker based)
   1. Locally - Same architecture as host
   2. Remotely - Public IP address or DNS reference


3. Ability to prepare/setup an existing remote host via SSH
   1. Install and configure docker


## Usage

- Consider passing json format for ssh and node parameters as text or as a file.
    - `ssh-info "{'port': 2222, 'jenkins-cred-id': 23lj3332}"`
    - `ssh-info ./ssh-info.json`

- Have set of common options, and option to pass in a json file

### Prepare Mode - HOLD OFF FOR NOW
```
yo-jenkins node prepare <HOST ADDRESS>
    --ssh-port <PORT NUMBER>
    --ssh-user <USERNAME>
    --ssh-public-key-file <KEY FILE PATH>
    --ssh-public-key-text <KEY TEXT>
    --system-type <ubuntu, amazonlinux, macos, windows>
    --custom-script <PATH TO SCRIPT>
```

### Permanent Mode
Only need to do api calls to Jenkins Server to set up.
```
yo-jenkins node setup-permanent [NAME] [HOST] [CRED_ID]
    --description <DESCRIPTION>
    --labels <LIST OF LABELS>
    --executors <NUMBER OF EXECUTORS>
    --mode <NORMAL or EXCLUSIVE>
    --retention <Always or Demand>
    --ssh-port <PORT NUMBER>
    --ssh-verify-type <VERIFY TYPE>
    --remote-java-path <PATH>
    --remote-root-dir <ROOT DIRECTORY>
    --config-file <PATH TO FILE>
```

### Ephemeral Mode
```
yo-jenkins node setup-ephemeral [NAME] [HOST] <--- can be "local"
  --labels linux,test
  --image my_repo/my_image:latest         <--- default image "jenkins/ssh-agent:alpine"
  --jenkins-home /home/jenkins
  --user root                             <--- If a custom image is used
  --public-key ~/.ssh/mykey               <--- (SSH credentials or location of private key)
```


---

## Manual Setup Process for Persistent Node

### Independently, setup agent host
   - Running in Docker container
     - Container on same host as master node
       - Install and configure docker
       - `export JENKINS_AGENT_SSH_PUBKEY="<PUBLIC KEY>"`
       - `docker run --rm --name jenkins-ssh-agent jenkins/ssh-agent $JENKINS_AGENT_SSH_PUBKEY`
-
     - Container on remote host **(FAILED SSH AUTHENTICATION)**
       - Install and configure docker
       - Ensure SSHD is running inside the container
       - If in cloud, ensure security groups allow inbound TCP port 2222
       - `export JENKINS_AGENT_SSH_PUBKEY="<PUBLIC KEY>"`
       - `docker run --rm --publish 2222:22 --name jenkins-ssh-agent jenkins/ssh-agent $JENKINS_AGENT_SSH_PUBKEY`
       - `ssh <USER>@<HOST> -p 2222`

   - Running on host OS
      - *(If needed)* Setup and start SSHD service as `root`
         - Ubuntu: `apt-get -y install openssh-server && systemctl enable ssh && systemctl start ssh`
         - AWSLinux: `yum -y install openssh-server && systemctl enable sshd && systemctl start sshd`
      - Install Java as `root` user
          - AWS EC2: `amazon-linux-extras install -y java-openjdk11 && which java`
      - Add `jenkins` user
        - `adduser jenkins --shell /bin/bash && awk -F: '{ print $1}' /etc/passwd`
      - Log in as `jenkins` user
        - `su jenkins`
      - Create `authorized_keys` file
        - `mkdir -p /home/jenkins/.ssh`
      - Add public key to `authorized_keys` file
        - `echo "<PUBLIC KEY>" >> home/jenkins/.ssh/authorized_keys`
        - Or copy existing authorized keys file to jenkins user
      - Assign the right permissions
        - `chmod 0700 /home/jenkins/.ssh`
        - `chmod 0600 /home/jenkins/.ssh/authorized_keys`

### Setup the agent in Jenkins Server
   - Go to: Manage Jenkins > Manage Nodes and Clouds > Add Node
   - Permanent Node
   - Remote Root Directory: `/home/jenkins`
   - Launch agents with SSH
      - Host: IP or DNS of the agent host
        - If local Docker container, specify the IP of the container:
          - `docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER>`
      - Credentials: Add private key in Jenkins credentials
        - User: jenkins
        - SSH Private Key
      - Host Key Verification Strategy
         - Local Docker: No host key verification strategy
         - Remote System: Manually trusted verification strategy
      - Advanced -> Java Path: Path to host's java binary (ie. `/usr/bin/java`)


## Manual Setup Process for Ephemeral Node

1. Manage Jenkins > Manage Nodes and Clouds > Configure Clouds

2. Docker Cloud Details
   - Docker Host URI: `unix:///var/run/docker.sock`
   - Enabled
   - Advanced > Docker Hostname or IP address: `172.17.0.1` (Host IP for Docker Gateway)
   - Test Connection

3. Docker Agent Templates...
   - Docker Image: `jenkins/ssh-agent`
     - Must have SSHD running
     - Must have Java installed
   - Connect with SSH
     - Inject SSH Key
       - User: `jenkins`
       - Advanced > JavaPath: `/usr/local/openjdk-8/bin/java`
     - Use configured SSH Credentials **(DID NOT WORK)**
       - SSH Credentials: Private key is stored in Jenkins credentials
       - Host Key Verification Strategy: Known hosts file Verification Strategy
   - Node Properties
     - Environment Variables: `JENKINS_AGENT_SSH_PUBKEY`: `[YOUR PUBLIC KEY]`
     - NOTE: Check out how `jenkins/ssh-agent` is using this environment variable


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
2. Adding a persistent agent to jenkins with yo-jenkins

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

- COnfigure Cloud - Docker
  - Connect with JNLP
  - Attach Docker container
    - https://www.bogotobogo.com/DevOps/Docker/Docker-Jenkins-Master-Slave-Agent-ssh.php
    - Image Used: jenkins/inbound-agent

- AWS EC2 Instance:
  - Create
    ```
    aws ec2 run-instances \
        --image-id ami-0c2b8ca1dad447f8a \
        --count 1 \
        --instance-type t2.micro \
        --key-name aws-key-1 \
        --security-group-ids sg-5dd41e7a \
        --subnet-id subnet-5b44903d \
        --user-data file:///home/ismet/Projects/yo-jenkins/yo_jenkins/resources/scripts/node_prepare_amazonlinux2.sh
    ```
  - SSH in
    ```
    ssh -i /home/ismet/.ssh/aws-key-1.pem \
        -o StrictHostKeyChecking=no \
        ec2-user@$(aws ec2 describe-instances \
        | jq -r '.Reservations[].Instances[] | select(.State.Name == "running").PublicDnsName')
    ```
  - Remove the running instance
    ```
    aws ec2 terminate-instances \
        --instance-ids $(aws ec2 describe-instances \
        | jq -r '.Reservations[].Instances[] | select(.State.Name == "running").InstanceId')
    ```

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

- Docker on AWS Linux
  - `amazon-linux-extras install -y docker && yum install -y docker && service docker start && usermod -a -G docker jenkins && logout`

- As root, setup and configure `jenkins` user
  - `adduser jenkins --shell /bin/bash && awk -F: '{ print $1}' /etc/passwd`
  - `su jenkins`
  - `mkdir -p /home/jenkins/.ssh && touch home/jenkins/.ssh/authorized_keys`
  - `chmod 0700 /home/jenkins/.ssh && chmod 0600 /home/jenkins/.ssh/authorized_keys`
