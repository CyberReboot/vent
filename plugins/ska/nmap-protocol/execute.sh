#!/usr/bin/env bash

count=0
{ read; while read line
do
  array_line=(${line//,/ })
  ip="${array_line[1]}"
  cmd="{\"Image\":\"zka/nmap\", \"HostConfig\": {\"VolumesFrom\":[\"visualization-honeycomb\"]}, \"Cmd\":[\"nmap\", \"-F\", \"-oN\", \"/honeycomb-data/nmap-protocol-data/$ip.log\", \"$ip\"]}"
  echo "$cmd"

  one="echo -e 'POST /containers/create HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 1023\r\n\r\n$cmd'"
  container_id=$(eval $one | nc -U /var/run/docker.sock | tail -1 | jq '.Id')
  echo "$container_id"
  two="echo -e \"POST /containers/${container_id:1:${#container_id}-2}/start HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n{}'\" | nc -U /var/run/docker.sock"
  eval $two

  if [ "$count" -gt 5 ]; then
    sleep 15
    count=0
  fi
  ((count++))
done } < output.csv
