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

Or, if you need to tell the Docker daemon to use a specific DNS server, add the· 
following to ``/var/lib/boot2docker/profile``:

```
EXTRA_ARGS="--dns 192.168.1.2"
```
