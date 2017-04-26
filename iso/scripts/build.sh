#!/bin/bash

# get latest boot2docker
docker pull boot2docker/boot2docker || exit 1

# get latest python2
cd vendor/tinycore-python2
rm -rf python2.tar
#docker pull cyberreboot/tce-python
docker build -t cyberreboot/tce-python . || exit 1
docker run --rm cyberreboot/tce-python > python2.tar || exit 1

# get latest vent-management
cd -
cd vent/core/management
rm -rf vent-management.tar
#docker pull cyberreboot/vent-management
docker build -t cyberreboot/vent-management . || exit 1
docker save -o vent-management.tar cyberreboot/vent-management || exit 1

echo "successfully finished building everything."
