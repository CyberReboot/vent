#!/usr/bin/env bash

path=$1
count=0

while [ ! -f $path ]
do
  sleep 2
done

sleep 5
mkdir -p /honeycomb-data/nmap-protocol-data

{ read; while read line
do
  array_line=(${line//,/ })
  ip="${array_line[1]}"
  cmd="{\"Image\":\"zka/nmap\", \"HostConfig\": {\"VolumesFrom\":[\"1visualization-honeycomb\"]}, \"Cmd\":[\"nmap\", \"-F\", \"-oN\", \"/honeycomb-data/nmap-protocol-data/$ip.log\", \"$ip\"]}"
  echo "$cmd"

  one="echo -e 'POST /containers/create HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 1023\r\n\r\n$cmd'"
  container_id=$(eval $one | nc -U /var/run/docker.sock | tail -1 | jq '.Id')
  echo "$container_id"
  two="echo -e \"POST /containers/${container_id:1:${#container_id}-2}/start HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n{}'\" | nc -U /var/run/docker.sock"
  eval $two

  if [ "$count" -gt 10 ]; then
    sleep 60
    count=0
  fi
  ((count++))
done } < $path

flag=0
ports=0
cd /honeycomb-data/nmap-protocol-data
awk '{print $0","}' $path
sed -i '1s/$/,protocols/' $path
for i in *.log; do
  protocols="${i%.*},\"["
  while read line
  do
    if [ "$flag" -eq 6 ]; then
      ports=1
    fi
    if [ "$ports" -eq 1 ]; then
      if [ "$line" != "" ]; then
        csv=$(echo "$line"|awk -v OFS="," '$1=$1')
        arr_csv=(${csv//,/ })
        protocols="$protocols{\\\"port\\\":\\\"${arr_csv[0]}\\\",\\\"state\\\":\\\"${arr_csv[1]}\\\",\\\"service\\\":\\\"${arr_csv[2]}\\\"},"
      else
        ports=0
      fi
    fi
    ((flag++))
  done < $i
  j=$((${#protocols}-1))
  if [ "${protocols:$j:1}" == "," ]; then
    protocols="${protocols::$j}]\""
  else
    protocols="$protocols]\""
  fi
  echo "protocols: $protocols"

  arr_protocol=(${protocols/,/ })
  echo "array: $arr_protocol"

  COUNT=0
  while read -r li; do
      COUNT=$(( $COUNT + 1 ))
      if [[ $li == *"${i%.*}"* ]];then
          echo "inside: $li"
          cmd="sed -i '$COUNTs/\$/${arr_protocols[1]}/' $path"
          eval $cmd
      fi
  done < $path
done

cmd="cd /dns-data; git commit -a -m \"update dns records\";";
eval $cmd;

echo "done"
