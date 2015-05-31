#!/bin/bash

cd dependencies/tinycore-python2
echo "building python for tinycore linux..."
if [ "$1" == "--no-cache" ]; then
    docker build --no-cache -t tce-python .
else
    docker build -t tce-python .
fi
docker run --rm tce-python > python2.tar
cd -
echo "building vent..."
if [ "$1" == "--no-cache" ]; then
    docker build --no-cache -t vent .
else
    docker build -t vent .
fi
docker run --rm vent > vent.iso
rm -rf dependencies/tinycore-python2/python2.tar
echo "done..."
