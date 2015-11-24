#!/bin/sh

image_exists=$(docker images -q vent-management | wc -l)
if [ "$image_exists" == "0" ]; then
	docker load -i /data/management/vent-management.tar
fi
exists=$(docker ps -aq --filter name=vent-management | wc -l)
if [ "$exists" == "1" ]; then
	docker start vent-management
else
	docker run --name vent-management -d -v /mnt/sda1/var/lib/boot2docker/tls:/certs -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp vent-management
fi
