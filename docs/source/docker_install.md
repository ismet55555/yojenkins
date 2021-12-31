# Docker Installation Guide

This document outlines how to install Docker on various operating systems.


## MacOS

Either of these following options will install Docker in your MacOS system:

- [Docker Desktop installation](https://docs.docker.com/docker-for-mac/install/)
- Using homebrew (`brew`) package manager
    - `brew cask install docker`


## Windows

Either of these following options will install Docker in your Windows system:

- [Docker Desktop installation](https://docs.docker.com/docker-for-windows/install/)
- Using Chocolatey package manager
    - `choco install docker-desktop`


## Ubuntu

Run the following commands in order to install Docker in your Ubuntu system:

```bash
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```


## CentOS / AmazonLinux2

Run the following commands in order to install Docker in your CentOS / AmazonLinux2 system:

```bash
sudo amazon-linux-extras install -y docker
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker <YOUR USERNAME>
```
