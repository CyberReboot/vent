vent
====

> Network Visibility (an anagram)

[![CircleCI](https://circleci.com/gh/CyberReboot/vent.svg?style=shield)](https://circleci.com/gh/CyberReboot/vent)
[![Documentation Status](https://readthedocs.org/projects/vent/badge/?version=latest)](http://vent.readthedocs.io/en/latest/?badge=latest)
[![GitHub Release](https://badge.fury.io/gh/cyberreboot%2Fvent.svg)](https://github.com/CyberReboot/vent/releases)
[![codecov](https://codecov.io/gh/CyberReboot/vent/branch/master/graph/badge.svg)](https://codecov.io/gh/CyberReboot/vent)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/ffe3b2d6a9254b98a12de6b3273676b3/badge.svg)](https://www.quantifiedcode.com/app/project/ffe3b2d6a9254b98a12de6b3273676b3)
[![Github Release Downloads](https://img.shields.io/github/downloads/cyberreboot/vent/total.svg?maxAge=2592000)](https://github.com/CyberReboot/vent/releases)

            '.,
              'b      *
               '$    #.
                $:   #:
                *#  @):
                :@,@):   ,.**:'
      ,         :@@*: ..**'
       '#o.    .:(@'.@*"'
          'bq,..:,@@*'   ,*
          ,p$q8,:@)'  .p*'
         '    '@@Pp@@*'
               Y7'.'
              :@):.
             .:@:'.
           .::(@:. 
                       _   
      __   _____ _ __ | |_ 
      \ \ / / _ \ '_ \| __|
       \ V /  __/ | | | |_ 
        \_/ \___|_| |_|\__|

overview
====
vent is a lightweight, self-contained virtual appliance designed to serve as a general platform for analyzing network traffic. built with some basic functionality, vent serves as a user-friendly slate to build custom `plugins` on to perform user-defined processing on incoming network data. vent supports any filetype, but only processes one based on the types of plugins installed for that instance of vent.

simply create your `plugins`, point vent to them & install them, and drop a file in vent to begin processing!

download pre-compiled ISO
====

[releases](https://github.com/CyberReboot/vent/releases)


build the ISO
====

### build dependencies

```
docker
make
zip
```

### getting the bits

```
git clone --recursive https://github.com/CyberReboot/vent.git
cd vent
```

### building

```
make
```

easy ways to build a VM out of the ISO
====

with docker-machine cli:

```
# in a terminal from the path where the ISO file is (usually inside of the vent directory)
python -m SimpleHTTPServer

# from another terminal while the previous command is still running, execute the
# following, with optional additional arguments prior to the last vent in the command
docker-machine create -d virtualbox --virtualbox-boot2docker-url http://localhost:8000/vent.iso vent
# other options to customize the size of the vm are available as well:
# --virtualbox-cpu-count "1"
# --virtualbox-disk-size "20000"
# --virtualbox-memory "1024"

# finally once the previous command is finished, execute this for the vent user interface
docker-machine ssh vent
```

of course traditional ways of deploying an ISO work as well, including VMWare, OpenStack, and booting from it to install on bare metal.  a couple of things to note: it will automatically install and provision the disk and then restart when done.  vent runs in RAM, so changes need to be made under `/var/lib/docker` or `/var/lib/boot2docker` as those are persistent (see boot2docker [documentation](https://github.com/boot2docker/boot2docker/blob/master/README.md) for more information).  it's possible that `vent-management` won't automatically get added and run, if you run `docker ps` and it's not running, execute `sudo /vent/custom`.

getting started
====

from within the vent interface (once SSH'd in) first `build` the core.  it might take a little while to download and compile everything. `note` - you must build core before building any `plugins`, `collectors`, or `visualization`. core provides essential services needed to build/start other services.

once it's built you're ready to start the `core` from the `mode` menu option.

if you're using Virtualbox, before starting the `core` you'll want to first uncomment the `public_nic` option in the `core.template` by removing the `#` so that it uses `eth1` instead of the default `eth0`.  you can change this through the menu by going to  `Mode -> Configure`.

after starting, you should be able to go into `system info` and see that everything is running as expected.  once that looks good, you're ready to install plugins (again in the vent interface, under the plugins menu).  here's an example one that can handle PCAP files: https://github.com/CyberReboot/vent-plugins

once you're finished installing plugins, you're ready to copy up files to be processed, in the case of the above example plugin, you'd want to copy up PCAP files.  see below for how to do that, but once the files are copied up, they are automatically processed, sent as messages on a queue and indexed for quick and easy analysis.

copy up new pcaps
====

install the `vent` script locally first:
```
sudo make install
```

if using docker-machine cli to provision:

```
# from the directory that contains your pcaps
# optionally add an argument of the name for vent in
#     docker-machine if you called it something other than vent
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
scp modes.template docker@vent:/var/lib/docker/data/templates/modes.template
```

package installation for development (experimental)
====
- clone the repository

`$ git clone --recursive https://github.com/CyberReboot/vent`
- running setup.py

`$ python setup.py install`

documentation
====

- [Docs](https://github.com/CyberReboot/vent/tree/master/docs)
- [Diagrams](https://github.com/CyberReboot/vent/tree/master/docs/images)

contributing to vent
====

Want to contribute?  Awesome!  Issue a pull request or see more details [here](https://github.com/CyberReboot/vent/blob/master/CONTRIBUTING.md).

FAQ
====

**Q**: What are the credentials to login if I don't use certificates/keys?

**A**: docker/tcuser

**Q**: I went into the shell and did a `docker ps` but no containers are running, how do I get it working again?

**A**: Execute `docker rm vent-management; sudo /vent/custom`, if that doesn't work, restart the machine.

**Q**: I'm not running DHCP, how do I statically set the IP Address?

**A**: For a quick and dirty solution (doesn't survive reboot):

```
ifconfig eth0 192.168.99.101 netmask 255.255.255.0 broadcast 192.168.99.255 up
ip route add default via 192.168.99.1
```

Additionally if you need to set DNS, add the following to `/etc/resolv.conf`:

```
nameserver 8.8.8.8
```

For a more permanent solution look at the [docs](https://github.com/boot2docker/boot2docker) for boot2docker
