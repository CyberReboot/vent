vent
====

> Network Visibility (an anagram)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/792bc7e54645427581da66cd6847cc31)](https://www.codacy.com/app/clewis/vent?utm_source=github.com&utm_medium=referral&utm_content=CyberReboot/vent&utm_campaign=badger)
[![Build Status](https://travis-ci.org/CyberReboot/vent.svg?branch=master)](https://travis-ci.org/CyberReboot/vent)
[![Documentation Status](https://readthedocs.org/projects/vent/badge/?version=latest)](http://vent.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/vent.svg)](https://badge.fury.io/py/vent)
[![codecov](https://codecov.io/gh/CyberReboot/vent/branch/master/graph/badge.svg)](https://codecov.io/gh/CyberReboot/vent)
[![Docker Hub Downloads](https://img.shields.io/docker/pulls/cyberreboot/vent-elasticsearch.svg)](https://hub.docker.com/u/cyberreboot)

![Vent Logo](/docs/img/vent-logo.png)

overview
====
vent is a library that includes a CLI designed to serve as a general platform for analyzing network traffic. Built with some basic functionality, vent serves as a user-friendly platform to build custom `plugins` that perform user-defined processing on incoming network data. vent is filetype-agnostic in that the plugins installed within your specific vent instance determine what type of files your instance supports.

Simply create your `plugins`, point vent to them & install them, and drop a file in vent to begin processing!

### dependencies

```
docker>=1.13.1
git
make (if building from source)
pip
python2.7.x
```

### option 1: running inside of a Docker container

```
docker run -it -v /var/run/docker.sock:/var/run/docker.sock cyberreboot/vent
```

### option 2: installing

```
pip install vent
```

### option 3: getting the bits and building

```
git clone https://github.com/CyberReboot/vent.git
cd vent
```

Root/sudo users can simply run `make` to compile and install the platform.  Users with limited permissions or require user-local installation can use the following:

```
sudo env "PATH=$PATH" make
```

_Note - If you already have `docker-py` installed on your machine, you may need to_ `pip uninstall docker-py` _first. `vent` will install `docker-py` as part of the installation process, however there are known incompatibilities of `docker-py` with older versions._

### option 4: deploying with an ISO

go to [releases](https://github.com/CyberReboot/vent/releases) and download the ISO from the latest release (or build your own: `cd dev && make`)
deploy the ISO as a VM or on bare metal.

### running

```
vent
```
documentation
====
Want to read the documentation for vent?  Great! You can find it [here](https://vent.readthedocs.io/en/latest/?badge=latest)

contributing to vent
====

Want to contribute?  Awesome!  Issue a pull request or see more details [here](https://github.com/CyberReboot/vent/blob/master/CONTRIBUTING.md).

See [this](https://media.readthedocs.org/pdf/npyscreen/latest/npyscreen.pdf) for a crash course on npyscreen: the TUI used by Vent!
