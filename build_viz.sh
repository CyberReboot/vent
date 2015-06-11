#!/bin/sh

if [ "$1" == "--no-cache" ]; then
	cd /data/visualization && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t visualization/$(echo {} | sed 's%^.\/%%') .)' ';'
	docker images | grep none | awk '{print $3}' | xargs docker rmi
else
	cd /data/visualization && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t visualization/$(echo {} | sed 's%^.\/%%') .)' ';'
	docker images | grep none | awk '{print $3}' | xargs docker rmi
fi
