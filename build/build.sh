#!/bin/bash

# !! TODO add flag to run with --no-cache

cd dependencies/tinycore-python2
echo "building python for tinycore linux..."
docker build -t tce-python .
docker run --rm tce-python > python2.tar
cd -
echo "building vent..."
docker build -t vent .
docker run --rm vent > vent.iso
rm -rf dependencies/tinycore-python2/python2.tar
echo "done..."
