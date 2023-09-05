# package-resolver

This package is for those who need to download a package, with ALL of its dependencies. Not install, download only.

The idea is to be able to get all versions, of any package, on all platforms. This includes:

- Linux distros packages (deb, rpm, apk...)
- Programming languages packages (Python, Node...)

## OS Distributions

At the moment only Ubuntu, Centos and alpine are implemented, all at their latest versions.
In the future you will be able to get packages based on the distro version.

## Programming languages packages

At the moment only python and node are implemented, But in the future you will be able to download packages based on the language version, and os distro.

## Requirements

The problem is that you can't download rpm files with yum if you are on ubuntu. Right? Wrong. This is possible thanks to docker containers.
You can build any environment imaginable with containers, and thats what this package does.
If you want to download vim for ubuntu, no matter what os you are running, the package will run a container of ubuntu, download the .deb files and zip it to one single file.

**To use this package you will need to run docker on your system: [Install Docker](https://docs.docker.com/get-docker/)**

## Installation

```bash
    $ python -m pip install all-package-resolver
```

## Usage

```bash
    $ download-package [OPTIONS] COMMAND [ARGS]...
```

### Options

```
    -v, --verbose                     Show logs
    -o, --output-dir <output-dir>     Output directory
    -c, --no-cleanup                  No cleanup
    -h, --help                        output usage information
```

### Commands

```
    os <distro> <package>  Download a package for a specific os distro
    lang <language> <lang-version> <package>  Download a package for a specific language
```

### Examples

```bash
    $ download-package os ubuntu vim
    $ download-package -v lang python 3.10 boto3
    $ download-package --output-dir="/dst/folder" lang python 3.6 boto3
    # For multiple packages
    $ download-package lang python 3.6 "boto3 requests"

    $ download-package --help
```
