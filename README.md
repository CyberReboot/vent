vent
====

Network Visibility (an anagram)

build the ISO
====

```
cd vent
./build.sh
```

easy ways to build a VM out of the ISO
====

with boot2docker cli:

```
cp vent.iso ~/.boot2docker/boot2docker.iso
# this step will probably take about 10 minutes, don't be alarmed if it says it
# can't connect to the docker socket, it's still building, give it a bit of time
boot2docker init; boot2docker up
boot2docker ssh
```

with docker-machine cli:

```
python -m SimpleHTTPServer
docker-machine create -d virtualbox --virtualbox-boot2docker-url http://localhost:8000/vent.iso vent
docker-machine ssh vent
```

copy up new templates and plugins
====

if using boot2docker cli to provision:

```
scp -r -i ~/.ssh/id_boot2docker -P 2022 modes.template docker@localhost:/data/templates/modes.template
```

if using docker-machine cli to provision:

```
XXX TODO
```
