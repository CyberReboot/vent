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
which will build the Vent ISO that can be deployed as a VM or on a bare metal server.
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

Summary of stuff.

Makefile options
----

Summary of stuff.

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

Summary of stuff.

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


