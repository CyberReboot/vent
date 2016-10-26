#!/bin/bash

# !! TODO this script is pretty brittle, it should do better error checking

# !! TODO have a flag for --build-plugins to build plugins on the first boot
#rm -rf vent-*.iso

# commentted out a bunch of lines because bootstrapped

#echo "building python for tinycore linux..."
#if [ "$1" = "--no-cache" -o "$2" = "--no-cache" ]; then
#    docker build --no-cache -t tce-python .
#else
#    docker build -t tce-python .
#fi

# get latest boot2docker
docker pull boot2docker/boot2docker

cd vendor/tinycore-python2
docker pull cyberreboot/tce-python
docker run --rm cyberreboot/tce-python > python2.tar

#echo "building vent-management..."
#if [ "$1" = "--no-cache" -o "$2" = "--no-cache" ]; then
#    docker build --no-cache -t vent-management .
#else
#    docker build -t vent-management .
#fi

cd -
cd vent/management
docker pull cyberreboot/vent-management
docker save -o vent-management.tar cyberreboot/vent-management

echo "done..."
cd -
if [ "$1" = "--build-plugins" -o "$2" = "--build-plugins" ]; then
    echo "building plugins...this might take a while, and a couple GB of space..."
    if [ "$1" = "--no-cache" -o "$2" = "--no-cache" ]; then
        ./scripts/build_images.sh --no-cache --save
    else
        ./scripts/build_images.sh --save
    fi
    mkdir -p images
    mv /tmp/vent-*.tar images/
fi
echo "building vent..."
#if [ "$1" == "--no-cache" || "$2" == "--no-cache"]; then
#    docker build --no-cache -t vent .
#else
#    docker build -t vent .
#fi
#docker run --rm vent > vent.iso
#rm -rf dependencies/tinycore-python2/python2.tar
#rm -rf management/vent-management.tar
#echo "done..."
