#!/bin/sh

if [ "$1" = "--no-cache" -o "$2" = "--no-cache" ]; then
	if [ "$1" = "--save" -o "$2" = "--save" ]; then
		cd core && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t core/$(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-core-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar core/$(echo {} | sed 's%^.\/%%'))' ';'
        cd ..
	else
		cd /var/lib/docker/data/core && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t core/$(echo {} | sed 's%^.\/%%') .)' ';'
	fi
else
	if [ "$1" = "--save" -o "$2" = "--save" ]; then
		cd core && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t core/$(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-core-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar core/$(echo {} | sed 's%^.\/%%'))' ';'
        cd ..
	else
		cd /var/lib/docker/data/core && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t core/$(echo {} | sed 's%^.\/%%') .)' ';'
	fi
fi
