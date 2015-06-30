#!/usr/bin/env sh
running=$(docker ps --filter="name=visualization-honeycomb" | wc -l); if [ $running == "2" ]; then echo "http://$(/sbin/ifconfig eth1 | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}'):$(docker inspect -f '{{range $p, $conf := .NetworkSettings.Ports}}{{(index $conf 0).HostPort}} {{end}}' visualization-honeycomb)"; else echo "not running"; fi
