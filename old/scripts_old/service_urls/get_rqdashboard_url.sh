#!/usr/bin/env sh
/sbin/ifconfig -a|grep ^eth1 &>/dev/null && interface=eth1
if [ -z "$interface" ]; then ip=$(/usr/local/sbin/ss | grep ssh | awk '{print $5}' | cut -d ':' -f 1); else ip=$(/sbin/ifconfig eth1 | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}'); fi
running=$(docker ps --filter="name=core-rq-dashboard" | wc -l); if [ $running == "2" ]; then echo "http://$ip:$(docker inspect -f '{{range $p, $conf := .NetworkSettings.Ports}}{{(index $conf 0).HostPort}} {{end}}' core-rq-dashboard | awk '{print $1}')/rq"; else echo "not running"; fi
