"""Installation/Packaging Definition for Python Project"""

import os
import sys

import setuptools

# Package version number (Updated via bump2version tool)
__version__ = "0.0.68"

def check_py_version():
    """Check the python version"""
    if sys.version_info < (3, 7):
        print('Your Python version ({}.{}) is not supported'.format(sys.version_info.major, sys.version_info.minor))
        print('You must have Python version 3.7 or higher to run this program')
        if sys.version_info.major < 3:
            print('You may have used "python" where you needed to use "python3"?')
        sys.exit(1)

def get_requirements():
    """Load packages from requirements.txt"""

    check_py_version()

    with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as handle:
        packages = handle.readlines()
    packages = [package.strip() for package in packages]

    return packages

def get_pipfile_requirements():
    """Load packages from Pipfile"""
    from toml import loads

    # Loading Pipfile
    try:
        with open ('Pipfile', 'r') as open_file:
            pipfile = open_file.read()
        pipfile_toml = loads(pipfile)
    except FileNotFoundError:
        return []

    # Getting the "packages section"
    try:
        required_packages = pipfile_toml['packages'].items()
    except KeyError:
        return []

    # Parsing Pipfile
    packages = []
    for package_name, ver in required_packages:
        version = ver
        if not isinstance(ver, str):  # Check for a dict
            version_parts = []
            if 'version' in ver:
                version_parts.append(ver['version'] if ver['version'] != '*' else "")
            if 'platform_system' in ver:
                version_parts.append(f"platform_system {ver['platform_system']}")
            version = '; '.join(version_parts)
        packages.append(package_name if version == "*" else f"{package_name}{version}")
    return packages

def read(fname):
    """Utility function to read the README file. Used for the long_description"""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name="yojenkins",
    version=__version__,
    author="Ismet Handzic",
    author_email="ismet.handzic@gmail.com",
    maintainer="Ismet Handzic",
    description="A CLI tool to manage and have fun with Jenkins server",
    keywords="jenkins monitor manage job build fun",
    url="https://github.com/ismet55555/yojenkins",
    packages=setuptools.find_packages(),
    install_requires=get_requirements(),
    include_package_data=True,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    setup_requires=['wheel'],
    py_modules=["yojenkins"],
    entry_points={
        "console_scripts": [
                "yojenkins = yojenkins.__main__:main"
            ]
        },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Monitoring',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Environment :: Console",
        "Environment :: Console :: Curses",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
