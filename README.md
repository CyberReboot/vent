vent
====

Network Visibility (an anagram)

download pre-compiled ISO
====

[releases](https://github.com/CyberReboot/vent/releases)


build the ISO
====

### build dependencies

```
docker
```

### getting the bits

```
git clone https://github.com/CyberReboot/vent.git
cd vent
```

### `Makefile` targets

#### Disclaimer, the `prebuilt` version is currently kernel panicking and not included in `all`

There are two different variants of the build.  One that already has all of the needed containers prebuilt and included in the ISO, and one that does not.  Note the one with the containers built will take quite a while (~1 hour) to build and will be approximately 1.3GB, while the one without will be much quicker and only 40MB.

#### `make all`

This target (the default target if none is supplied) will build both the `minimal` and the `prebuilt` ISOs.

#### `make all-no-cache.iso`

This will build both ISOs, but it won't use cache.

#### `make vent-minimal.iso`

This target will build the minimal image without building the containers and build/extract the ISO from the final result.

#### `make vent-prebuilt.iso`

This target will build the prebuilt image including building all the containers and build/extract the ISO from the final result.

#### `make vent-<variant>-no-cache.iso`

This will build the same target for whichever variant, but it won't use cache.

#### `make clean`

This will remove all of the tarballs and ISOs created from any of the build processes.

easy ways to build a VM out of the ISO
====

with docker-machine cli:

```
python -m SimpleHTTPServer
docker-machine create -d virtualbox --virtualbox-boot2docker-url http://localhost:8000/vent-<variant>.iso vent
# other options to customize the size of the vm are available as well:
# --virtualbox-cpu-count "1"
# --virtualbox-disk-size "20000"
# --virtualbox-memory "1024"
docker-machine ssh vent
```

of course traditional ways of deploying an ISO work as well, including VMWare, OpenStack, and booting from it to install on bare metal.  a couple of things to note: it will automatically install and provision the disk and then restart when done.  vent runs in RAM, so changes need to be made under `/var/lib/docker` or `/var/lib/boot2docker` as those are persistent (see boot2docker [documentation](https://github.com/boot2docker/boot2docker/blob/master/README.md) for more information).  it's possible that `vent-management` won't automatically get added and run, if you run `docker ps` and it's not running execute `sudo /data/custom`.

getting started
====

from within the vent interface (once SSH'd in) first `build` the collectors (if you chose the `prebuilt` ISO this is already done for you, so you can skip this step).  it might take a little while to download and compile everything.

alternatively, if you want to access the vent interface from the console instead of SSHing in, you can run `vent` from the commandline.

once it's built you're ready to start the `collectors` from the `mode` menu option.

after starting, you should be able to go into `system info` and see that everything is running as expected.  once that looks good, you're ready to copy up pcaps.  that's it!

copy up new pcaps
====

if using docker-machine cli to provision:

```
# from the directory that contains your pcaps
# optionally add an argument of the name for vent in
#     docker-machine if you called it something other than vent
cd vent
cp vent /usr/local/bin/
cd /path/where/pcaps/are/
vent
```

if deploying as a self-configured machine (VMWare, OpenStack, bare metal, etc.):

```
# from the directory that contains your pcaps
# optionally add an argument of the name/ip for vent on your network
cd vent
cp vent-generic /usr/local/bin/vent
cd /path/where/pcaps/are/
vent
```

otherwise edit the `ssh` and `scp` lines in `vent` specific to docker-machine and change to suit your needs

copy up new templates and plugins
====

if using docker-machine cli to provision:

```
docker-machine scp modes.template vent:/var/lib/docker/data/templates/modes.template
```

if using boot2docker cli to provision (DEPRECATED):

```
scp -r -i ~/.ssh/id_boot2docker -P 2022 modes.template docker@localhost:/var/lib/docker/data/templates/modes.template
```

if deploying as a self-configured machine (VMWare, OpenStack, bare metal, etc.):

```
scp modes.template docker@vnet:/var/lib/docker/data/templates/modes.template
```

FAQ
====

**Q**: What are the credentials to login if I don't use certificates/keys?

**A**: docker/tcuser

**Q**: I went into the shell and did a `docker ps` but no containers are running, how do I get it working again?

**A**: execute `docker rm vent-management; sudo /data/custom`, if that doesn't work, restart the VM.

The following notes mirror that of [boot2docker](https://github.com/boot2docker/boot2docker)
====

#### Docker daemon options

If you need to customize the options used to start the Docker daemon, you can
do so by adding entries to the `/var/lib/boot2docker/profile` file on the
persistent partition inside the Boot2Docker virtual machine. Then restart the
daemon.

The following example will enable core dumps inside containers, but you can
specify any other options you may need.

```console
boot2docker ssh -t sudo vi /var/lib/boot2docker/profile
# Add something like:
#     EXTRA_ARGS="--default-ulimit core=-1"
boot2docker restart
```

#### Local Customisation (with persistent partition)

Changes outside of the `/var/lib/docker` and `/var/lib/boot2docker` directories
will be lost after powering down or restarting the boot2docker VM. However, if
you have a persistence partition (created automatically by `boot2docker init`),
you can make customisations that are run at the end of boot initialisation by
creating a script at ``/var/lib/boot2docker/bootlocal.sh``.

From Boot2Docker version 1.6.0, you can also specify steps that are run before
the Docker daemon is started, using `/var/lib/boot2docker/bootsync.sh`.

You can also set variables that will be used during the boot initialisation (after
the automount) by setting them in `/var/lib/boot2docker/profile`

For example, to download ``pipework``, install its pre-requisites (which you can
download using ``tce-load -w package.tcz``), and then start a container:

```
#!/bin/sh


if [ ! -e /var/lib/boot2docker/pipework ]; then
        curl -o /var/lib/boot2docker/pipework https://raw.github.com/jpetazzo/pipework/master/pipework
        chmod 777 /var/lib/boot2docker/pipework
fi

#need ftp://ftp.nl.netbsd.org/vol/2/metalab/distributions/tinycorelinux/4.x/x86/tcz/bridge-utils.tcz
#and iproute2 (and its friends)
su - docker -c "tce-load -i /var/lib/boot2docker/*.tcz"

#start my management container if its not already there
docker run -d -v /var/run/docker.sock:/var/run/docker.sock $(which docker):$(which docker)  -name dom0 svens-dom0
```

Or, if you need to tell the Docker daemon to use a specific DNS server, add the 
following to ``/var/lib/boot2docker/profile``:

```
EXTRA_ARGS="--dns 192.168.1.2"
```
