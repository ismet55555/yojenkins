# Docker Setup

This document outlines how to install Docker on your system

## MacOS
- Docker Desktop
    - https://docs.docker.com/docker-for-mac/install/

- homebrew
    ```bash
    brew cask install docker
    ```

## Windows
- Docker Desktop
    - https://docs.docker.com/docker-for-windows/install/

- Chocolatey
    ```
    choco install docker-desktop
    ```



## Ubuntu
```bash
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

## CentOS / AmazonLinux2
```bash
sudo amazon-linux-extras install -y docker
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker <USERNAME>
```