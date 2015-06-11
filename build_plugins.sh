#!/bin/sh

if [ "$1" == "--no-cache" ]; then
	cd /data/plugins && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t $(echo {} | sed 's%^.\/%%') .)' ';'
	cd /data/collectors && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t $(echo {} | sed 's%^.\/%%') .)' ';'
	docker images | grep none | awk '{print $3}' | xargs docker rmi
else
	cd /data/plugins && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t $(echo {} | sed 's%^.\/%%') .)' ';'
	cd /data/collectors && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t $(echo {} | sed 's%^.\/%%') .)' ';'
	docker images | grep none | awk '{print $3}' | xargs docker rmi
fi
