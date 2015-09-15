#!/bin/bash

# !! TODO this script is pretty brittle, it should do better error checking

# !! TODO have a flag for --build-plugins to build plugins on the first boot
rm -rf vent.iso

cd dependencies/tinycore-python2
echo "building python for tinycore linux..."
if [ "$1" == "--no-cache" ]; then
    docker build --no-cache -t tce-python .
else
    docker build -t tce-python .
fi
docker run --rm tce-python > python2.tar
cd -
cd management
echo "building vent-management..."
if [ "$1" == "--no-cache" ]; then
    docker build --no-cache -t vent-management .
else
    docker build -t vent-management .
fi
docker save -o vent-management.tar vent-management
echo "done..."
cd -
echo "building vent..."
if [ "$1" == "--no-cache" ]; then
    docker build --no-cache -t vent .
else
    docker build -t vent .
fi
docker run --rm vent > vent.iso
rm -rf dependencies/tinycore-python2/python2.tar
rm -rf management/vent-management.tar
echo "done..."
