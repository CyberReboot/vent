#!/bin/sh

basedir="/var/lib/docker/data"
if [ "$1" = "--basedir" ]; then
	basedir="$2";
	shift;
	shift;
fi

if [ "$1" = "--no-cache" -o "$2" = "--no-cache" ]; then
	if [ "$1" = "--save" -o "$2" = "--save" ]; then
		cd vent/core && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker pull cyberreboot/core-$(echo {} | sed 's%^.\/%%') && docker save -o /tmp/vent-core-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar cyberreboot/core-$(echo {} | sed 's%^.\/%%') && docker tag cyberreboot/core-$(echo {} | sed 's%^.\/%%') core/$(echo {} | sed 's%^.\/%%') || docker build --no-cache -t core/$(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-core-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar core/$(echo {} | sed 's%^.\/%%'))' ';'
		cd ..
		cd plugins && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t $(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar $(echo {} | sed 's%^.\/%%'))' ';'
		cd ..
		cd collectors && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t collectors/$(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-collectors-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar collectors/$(echo {} | sed 's%^.\/%%'))' ';'
		cd ..
		cd visualization && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t visualization/$(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-visualization-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar visualization/$(echo {} | sed 's%^.\/%%'))' ';'
		cd ../../scripts
	else
		cd $basedir/core && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && (docker pull cyberreboot/core-$(echo {} | sed 's%^.\/%%') && docker tag cyberreboot/core-$(echo {} | sed 's%^.\/%%') core/$(echo {} | sed 's%^.\/%%') || docker build --no-cache -t core/$(echo {} | sed 's%^.\/%%') .))' ';'
		cd $basedir/plugins && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t $(echo {} | sed 's%^.\/%%') .)' ';'
		cd $basedir/collectors && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t collectors/$(echo {} | sed 's%^.\/%%') .)' ';'
		cd $basedir/vent/visualization && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build --no-cache -t visualization/$(echo {} | sed 's%^.\/%%') .)' ';'
	fi
else
	if [ "$1" = "--save" -o "$2" = "--save" ]; then
		cd vent/core && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker pull cyberreboot/core-$(echo {} | sed 's%^.\/%%') && docker save -o /tmp/vent-core-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar cyberreboot/core-$(echo {} | sed 's%^.\/%%') && docker tag cyberreboot/core-$(echo {} | sed 's%^.\/%%') core/$(echo {} | sed 's%^.\/%%') || docker build -t core/$(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-core-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar core/$(echo {} | sed 's%^.\/%%'))' ';'
        cd ..
		cd plugins && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t $(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar $(echo {} | sed 's%^.\/%%'))' ';'
		cd ..
		cd collectors && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t collectors/$(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-collectors-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar collectors/$(echo {} | sed 's%^.\/%%'))' ';'
		cd ..
		cd visualization && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t visualization/$(echo {} | sed 's%^.\/%%') . && docker save -o /tmp/vent-visualization-$(echo {} | sed 's%^.\/%%' | sed 's%\/%-%').tar visualization/$(echo {} | sed 's%^.\/%%'))' ';'
		cd ../../scripts
	else
		cd $basedir/core && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && (docker pull cyberreboot/core-$(echo {} | sed 's%^.\/%%') && docker tag cyberreboot/core-$(echo {} | sed 's%^.\/%%') core/$(echo {} | sed 's%^.\/%%') || docker build -t core/$(echo {} | sed 's%^.\/%%') .))' ';'
		cd $basedir/plugins && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t $(echo {} | sed 's%^.\/%%') .)' ';'
		cd $basedir/collectors && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t collectors/$(echo {} | sed 's%^.\/%%') .)' ';'
		cd $basedir/visualization && find . -type d -exec sh -c '(cd {} && [ -f Dockerfile ] && echo {} && docker build -t visualization/$(echo {} | sed 's%^.\/%%') .)' ';'
	fi
fi
