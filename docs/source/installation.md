# Installation

[TOC]

---
## Install From Python Package Index (PYPI) Using `pip` *(Recommended)*

1.  Ensure python is installed and has compatible version
    * `python --version`
    * If it is not, install it: [Guide](https://realpython.com/installing-python/)
2.  Ensure that `pip` is installed
    - `pip --version`
    - If it is not, install it: [Guide](https://pip.pypa.io/en/stable/installation/)
3.  Install `yojenkins` from PYPI
    - `pip install yojenkins`
    - `pip install "yojenkins[sound]"` *(With monitor sound effects)*


## Install Using the Included `setup.py`

1. Download/Clone this entire `yojenkins` GitHub repository
2. Copy it to some temporary location on the computer you wish to install `yojenkins` on (ie. Downloads)
3. Open up a terminal on your computer
4. Use the `cd` and `cd ..` command to change directory into the new `yojenkins` directory
    * Example: `cd /home/username/Downloads/yojenkins`
5.  Ensure python is installed and has compatible version
    - `python --version`
    - If it is not, install it: [Guide](https://realpython.com/installing-python/)
6.  Ensure that `pip` is installed
    - `pip --version`
    - If it is not, install it: [Guide](https://pip.pypa.io/en/stable/installation/)
4.  Ensure that `pip`, `setuptools`, `wheel` are installed an up to date
    - `python -m pip install --upgrade pip setuptools wheel`
5.  Install `yojenkins` from PYPI
    - `python setup.py install`


## Download Pre-compiled Binary

1. Go to the releases page of the `yojenkins` GitHub repository:
    - [Releases Page](https://github.com/ismet55555/yojenkins/releases)
2. If available, download the latest pre-compiled binary for your operating system
    - Example: `yojenkins-0.0.00-linux-x86_64`, for Linux OS 64-bit Architecture
3. Move the binary to the a place where you can access it from the command line (ie. on `PATH`)

!!! note "Note"
    Not all operating systems and architectures are supported.
    As of now, only select and/or popular ones are.


## System Dependencies For Sound

The following system dependencies are needed for `yojenkins` to be able to play sound effects.
Sound effects are used for job and build monitor.

If you do not install these dependencies, `yojenkins` will still be able to function,
however it will not play any sound effects.

| Platform          | Command                                                                        |
| ----------------- | ------------------------------------------------------------------------------ |
| MacOS and Windows | Not needed                                                                     |
| Ubuntu            | `sudo apt update && apt-get install -y python3-dev python3-pip libasound2-dev` |
| CentOS            | `sudo yum update && yum install -y python3-devel gcc alsa-lib-devel`           |
