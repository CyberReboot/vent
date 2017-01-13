#!/bin/bash

# get latest boot2docker
docker pull boot2docker/boot2docker

# get latest python2
cd vendor/tinycore-python2
docker pull cyberreboot/tce-python
docker run --rm cyberreboot/tce-python > python2.tar

# get latest vent-management
cd -
cd vent/core/management
docker pull cyberreboot/vent-management
docker save -o vent-management.tar cyberreboot/vent-management
