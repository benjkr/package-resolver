# package-resolver

This package is for those who need to download a package, with ALL of its dependencies. Not install, download only.

The idea is to be able to get all versions, of any package, on all platforms. This includes:
* Linux distros packages (deb, rpm, apk...)
* Programming languages packages (Python, Node...)

## OS Distributions
At the moment only Ubuntu, Centos and alpine are implemented, all at their latest versions.
In the future you will be able to get packages based on the distro version.

## Programming languages packages
At the moment only python and node are implemented, But in the future you will be able to download packages based on the language version, and os distro.
For example: TensorFlow version x.x.x for Ubuntu 20.04 AND Python 3.8

## Requirements
The problem is that you can't download rpm files with yum if you are on ubuntu. Right? Wrong. This is possible thanks to docker containers.
You can build any environment imaginable with containers, and thats what this package does.
If you want to download vim for ubuntu, no matter what os you are running, the package will run a container of ubuntu, download the .deb files and zip it to one single file.

**To use this package you will need to run docker on your system: [Install Docker](https://docs.docker.com/get-docker/)**

## Usage
```bash
py main.py --show-logs language node 19 typeorm
py main.py --show-logs language python 3.10 numpy
py main.py --show-logs os alpine vim

# For help
py .\main.py --help
```
