
# vent

> Network Visibility (an anagram)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/792bc7e54645427581da66cd6847cc31)](https://www.codacy.com/app/clewis/vent?utm_source=github.com&utm_medium=referral&utm_content=CyberReboot/vent&utm_campaign=badger)
[![Build Status](https://travis-ci.org/CyberReboot/vent.svg?branch=master)](https://travis-ci.org/CyberReboot/vent)
[![Documentation Status](https://readthedocs.org/projects/vent/badge/?version=latest)](http://vent.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/vent.svg)](https://badge.fury.io/py/vent)
[![codecov](https://codecov.io/gh/CyberReboot/vent/branch/master/graph/badge.svg)](https://codecov.io/gh/CyberReboot/vent)
[![Docker Hub Downloads](https://img.shields.io/docker/pulls/cyberreboot/vent-elasticsearch.svg)](https://hub.docker.com/u/cyberreboot)

![Vent Logo](/docs/img/vent-logo.png)

## Overview

vent is a library that includes a CLI designed to serve as a general platform for analyzing network traffic. Built with some basic functionality, vent serves as a user-friendly platform to build custom `plugins` that perform user-defined processing on incoming network data. See this blog post - [Introducing vent](https://blog.cyberreboot.org/introducing-vent-1d883727b624)

## Dependencies

``` bash
docker>=1.13.1
git
make (if building from source)
pip3
python3.6.x
```

## Installation

### Option 1: Running inside of a Docker container

``` bash
docker run -it -v /var/run/docker.sock:/var/run/docker.sock cyberreboot/vent
```

### Option 2: Installing directly

``` bash
pip3 install vent
```

### Option 3: Getting the source and building

``` bash
git clone https://github.com/CyberReboot/vent.git
cd vent
```

Root/sudo users can simply run `make` to compile and install the platform.  Users with limited permissions or require user-local installation can use the following:

``` bash
sudo env "PATH=$PATH" make
```

_Note - If you already have `docker-py` installed on your machine, you may need to_ `pip uninstall docker-py` _first. `vent` will install `docker-py` as part of the installation process, however there are known incompatibilities of `docker-py` with older versions._

## Running

``` bash
vent
```

## Plugins

vent supports custom `plugins` that perform  user-defined processing on incoming data.

vent is filetype-agnostic in that the plugins installed within your specific vent instance determine what type of files your instance supports.  Simply create your `plugins`, point vent to them & install them, and drop a file in vent to begin processing!

The [vent-plugins](https://github.com/CyberReboot/vent-plugins) repository showcases a number of example plugins and contains details on how to create your own.

## Documentation

Want to read the documentation for vent?  Great! You can find it [here](https://vent.readthedocs.io/en/latest/?badge=latest)

## Contributing to vent

Want to contribute?  Awesome!  Issue a pull request or see more details [here](https://github.com/CyberReboot/vent/blob/master/CONTRIBUTING.md).

See [this](https://media.readthedocs.org/pdf/npyscreen/latest/npyscreen.pdf) for a crash course on npyscreen: the TUI used by Vent!
