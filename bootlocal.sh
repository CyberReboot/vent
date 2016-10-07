#!/bin/sh

image_exists=$(docker images -q cyberreboot/vent-management | wc -l)
if [ "$image_exists" == "0" ]; then
	docker load -i /vent/management/vent-management.tar
fi
exists=$(docker ps -aq --filter name=vent-management | wc -l)
if [ "$exists" == "1" ]; then
	docker start vent-management
else
	docker run --name vent-management --restart="always" -d -v /mnt/sda1/var/lib/boot2docker/tls:/certs -v /usr/local/bin/docker:/usr/local/bin/docker -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp cyberreboot/vent-management
fi
if [ -d "/var/lib/docker/data/images" ]; then
	echo "TERM=xterm LANG=C.UTF-8 /usr/local/bin/python2.7 /vent/menu_launcher.py" >> /root/.profile
	image_exists=$(docker images -q | wc -l)
	if [ "$image_exists" == "1" ]; then
		cd /var/lib/docker/data/images
		for i in `ls *.tar 1> /dev/null 2>&1`; do
			docker load -i "$i"
		done
	fi
	sudo rm -rf /var/lib/docker/data/images/*
fi
