#!/bin/bash

set -e

NEW_USERNAME=${1:-"jenkins"}
SSH_PUBLIC_KEY=${2:-"/home/ec2-user/.ssh/authorized_keys"}
JAVA_SETUP=${4:-true}
SSHD_SETUP=${3:-false}
DOCKER_SETUP=${5:-true}

# Checking if the user is root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Did you forget 'sudo'?"
   exit 1
fi

echo
echo "Script arguments:"
echo "  USERNAME:       ${NEW_USERNAME}"
echo "  SSH_PUBLIC_KEY: ${SSH_PUBLIC_KEY}"
echo "  JAVA_SETUP:     ${JAVA_SETUP}"
echo "  SSHD_SETUP:     ${SSHD_SETUP}"
echo "  DOCKER_SETUP:   ${DOCKER_SETUP}"


# SSHD (if needed)
if [ "$SSH_SETUP" = true ]; then
    echo "\n\n\n==============================================================="
    echo "Installing Open SSH ..."
    yum -y install openssh-server

    echo "Enabling and starting SSHD ..."
    systemctl enable sshd
    systemctl start sshd
fi


# Installing Java
if [ "$JAVA_SETUP" = true ]; then
    echo "\n\n\n==============================================================="
    echo "Installing Java ..."
    amazon-linux-extras install -y java-openjdk11
fi


# Setting up new user
echo "\n\n\n==============================================================="
echo "Creating new user: $NEW_USERNAME ..."
adduser jenkins --shell /bin/bash || true
grep $NEW_USERNAME /etc/passwd

echo "Adding user '$NEW_USERNAME' to sudoers ..."
echo "$NEW_USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

echo "Setting up user home and .ssh directory ..."
mkdir -p /home/$NEW_USERNAME/.ssh

echo "Copying public SSH key ..."
touch /home/$NEW_USERNAME/.ssh/authorized_keys

NEW_USER_PUB_KEY_LOCATION="/home/jenkins/.ssh/authorized_keys"

if test -f "$SSH_PUBLIC_KEY"; then
    echo "Copying contents of '$SSH_PUBLIC_KEY' into new location '$NEW_USER_PUB_KEY_LOCATION' ..."
    cat $SSH_PUBLIC_KEY >> $NEW_USER_PUB_KEY_LOCATION
else
    echo "Adding new SSH public key into '$NEW_USER_PUB_KEY_LOCATION' ..."
    echo "Public SSH key passed: $SSH_PUBLIC_KEY"
    echo $SSH_PUBLIC_KEY >> $NEW_USER_PUB_KEY_LOCATION
fi

echo "Assigning home directory persmisisons to user '$NEW_USERNAME'"
chown -R $NEW_USERNAME:$NEW_USERNAME /home/$NEW_USERNAME
chmod 700 /home/$NEW_USERNAME
chmod 600 /home/$NEW_USERNAME/.ssh/authorized_keys


# Installing Docker
if [ "$DOCKER_SETUP" = true ]; then
    echo "\n\n\n==============================================================="
    echo "Installing Docker ..."
    amazon-linux-extras install -y docker && yum install -y docker
    service docker start
    usermod -a -G docker $NEW_USERNAME
fi

echo
echo "Done!"
