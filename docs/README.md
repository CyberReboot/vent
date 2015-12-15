Vent Documentation
====

Summary of stuff.

Install instructions
====

For a pre-compiled ISO, skip down to the next [section](#install-instructions-download-the-release).

#### Build dependencies:
```
make
docker
```
#### Step 1 - Clone:
```
git clone https://github.com/CyberReboot/vent.git
cd vent
```
#### Step 2 - Make:

There are [several options](#install-instructions-makefile-options) of how to build `vent` from the Makefile.  
The easiest way to get started quickly is to just execute:
```
make
```
which will build the `vent` ISO that can be deployed as a VM or on a bare metal server.
#### Step 3 - Deploy:

This is just a standard ISO that can be deployed like any other ISO, but here is a simple way using [docker-machine](https://docs.docker.com/machine/) with a local virtualbox (`docker-machine` can also be used to deploy `vent` on cloud providers and data centers):
```
# from a terminal that is in the `vent` directory
# start a simple webserver to serve up the ISO file
python -m SimpleHTTPServer

# from another terminal run `docker-machine`
docker-machine create -d virtualbox --virtualbox-boot2docker-url http://localhost:8000/vent.iso vent
# other options to customize the size of the vm are available as well:
# --virtualbox-cpu-count "1"
# --virtualbox-disk-size "20000"
# --virtualbox-memory "1024"

# once it's done provisioning, the webserver from the first terminal can be stopped
# SSH into the vent CLI
docker-machine ssh vent
```
Now you're ready to [get started](#getting-started) using `vent`.

Download the release
----

The latest versioned releases are available for download [here](https://github.com/CyberReboot/vent/releases).  If you'd rather try out `vent` from the latest in master, it can be downloaded [here](https://github.com/CyberReboot/vent/releases).

Makefile options
----

The main target builds the `vent` ISO without any of the containers that will need to be built after the fact. This allows the ISO to be a mere 40MB.  If you use one of the `prebuilt` options it will also build all of the necessary containers and tarball them up.  You can then use the `vent` utility, after the `vent` instance is created, from inside the local `images` directory and specifying `tar` as an argument in order to add the tarballs as docker images on the instance.

#### `make all`

This target (the default target if none is supplied) will build the ISO.

#### `make all-no-cache`

This will build the ISO, but it won't use cache.

#### `make vent`

This target will build the minimal image without building the containers and build/extract the ISO from the final result.

#### `make vent-prebuilt`

This target will build the minimal image as well as tarballs of all of the images after building all the containers and build/extract the ISO from the final result.

#### `make vent-no-cache`

This will build the same target, but it won't use cache.

#### `make vent-prebuilt-no-cache`

This will build the same target and the tarballs, but it won't use cache.

#### `make images`

This will build the containers and export them as tarballs into the images directory and then make a zip of those tarballs.

#### `make install`

This will install `vent` and `vent-generic` into the path and can be used for loading in tarball images or copying up PCAPs or other files to a `vent` instance.

#### `make clean`

This will remove all of the tarballs and ISOs created from any of the build processes.

Getting Started
====

Summary of stuff.

Demo
----

Summary of stuff.

Tutorial
----

Summary of stuff.

Usage
----

Summary of stuff.

Use cases
----

Summary of stuff.

Advanced Usage
====

`vent` is based off of [boot2docker](https://github.com/boot2docker/boot2docker).  There are a few notable differences in the way this VM runs than a typical one might.  `vent` will automatically install and provision the disk on boot and then restart when done.  `vent` runs in RAM, so changes need to be made under `/var/lib/docker` or `/var/lib/boot2docker` as those are persistent (see boot2docker [documentation](https://github.com/boot2docker/boot2docker/blob/master/README.md) for more information).  it's possible that the `vent-management` container won't automatically get added and run, in order to remedy you can go to the shell from the `vent` CLI and run `docker ps` and if it's not running execute `sudo /data/custom`.

Commands
----

Summary of stuff.

Developers
====

Summary of stuff.

API
----

Summary of stuff.

Customizing
----

Summary of stuff.

Contributing
----

Summary of stuff.

Ecosystem
====

Summary of stuff.


