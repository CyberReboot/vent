#!/bin/sh

sleep 5
image_exists=$(docker images -q cyberreboot/vent-management | wc -l)
if [ "$image_exists" == "0" ]; then
	docker load -i /var/lib/docker/data/core/management/vent-management.tar
fi
exists=$(docker ps -aq --filter name=vent-management | wc -l)
if [ "$exists" == "1" ]; then
	docker start vent-management
else
	docker run --name vent-management --restart="always" -d -v /mnt/sda1/var/lib/boot2docker/tls:/certs -v /usr/local/bin/docker:/usr/local/bin/docker -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp cyberreboot/vent-management
fi
