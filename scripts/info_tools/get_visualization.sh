#!/usr/bin/env sh
/sbin/ifconfig -a|grep ^eth1 &>/dev/null && interface=eth1
if [ -z "$interface" ]; then ip=$(/usr/local/sbin/ss | grep ssh | awk '{print $5}' | cut -d ':' -f 1); else ip=$(/sbin/ifconfig eth1 | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}'); fi
for container in $(docker ps --filter="name=visualization" | sed -n '1!p' | awk '{print $NF}'); do running=$(docker ps --filter="name=$container" | wc -l); if [ $running == "2" ]; then echo "$container: http://$ip:$(docker inspect -f '{{range $p, $conf := .NetworkSettings.Ports}}{{(index $conf 0).HostPort}} {{end}}' $container)"; else echo "$container: not running"; fi; done
