#!/usr/bin/env sh
running=$(docker ps --filter="name=collectors-rq-dashboard" | wc -l); if [ $running == "2" ]; then echo "http://$(/sbin/ifconfig eth1 | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}'):$(docker inspect -f '{{range $p, $conf := .NetworkSettings.Ports}}{{(index $conf 0).HostPort}} {{end}}' collectors-rq-dashboard | awk '{print $1}')/rq"; else echo "not running"; fi
