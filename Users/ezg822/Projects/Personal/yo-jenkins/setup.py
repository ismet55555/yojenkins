#!/usr/bin/env python3

import os
import setuptools

# Package version number (Updated via bumpversion)
__version__ = "0.1.2"


def read(fname):
    """Utility function to read the README file. Used for the long_description"""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements():
    """Load packages in requirements.txt"""
    with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as handle:
        packages = handle.readlines()
    packages = [package.strip() for package in packages]

    return packages


setuptools.setup(
    name="yo-jenkins",
    version=__version__,
    author="Ismet Handzic",
    author_email="ismet.handzic@gmail.com",
    maintainer="Ismet Handzic",
    description="A tool to monitor, manage, and have fun with Jenkins server",
    keywords="jenkins monitor manage job build fun",
    url="NOT.SET.UP.YET.com",
    packages=setuptools.find_packages(),
    install_requires=requirements(),
    include_package_data=True,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    setup_requires=['wheel'],
    py_modules=["yo_jenkins"],
    entry_points={
        "console_scripts": [
                "yo-jenkins = yo_jenkins.__main__:main"
            ]
        },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: XXXXXXXXXX',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Intended Audience :: XXXXXXXXXX',
        'Topic :: XXXXXXXXXX',
        'Topic :: XXXXXXXX :: Testing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Environment :: Console",
        "Environment :: Console :: Curses",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
