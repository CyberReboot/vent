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
    exists="echo -e 'GET /containers/json?all=1&filters={%22status%22:[%22exited%22]} HTTP/1.0\r\n\r\n'"
    container_id=$(eval $exists | nc -U /var/run/docker.sock | tail -1 | jq '.[].Id')
    echo "$container_id" | while read li; do remove="echo -e 'DELETE /containers/${li:1:${#li}-2} HTTP/1.0\r\n\r\n' | nc -U /var/run/docker.sock"; eval $remove; done
    sleep 60
    count=0
  fi
  ((count++))
done } < $path

ports=0
cd /honeycomb-data/nmap-protocol-data
sed -i 's/$/,/' $path
sed -i '1s/$/protocols\n/' $path
first="yes"
for i in *.log; do
  protocols="${i%.*},\"["
  while read line
  do
    if [ "$ports" -eq 1 ]; then
      if [ "$line" != "" ]; then
        csv=$(echo "$line"|awk -v OFS="," '$1=$1')
        arr_csv=(${csv//,/ })
        protocols="$protocols{\\\"port\\\":\\\"${arr_csv[0]}\\\",\\\"state\\\":\\\"${arr_csv[1]}\\\",\\\"service\\\":\\\"${arr_csv[2]}\\\"},"
      else
        ports=0
      fi
    fi
    if [[ $line == PORT* ]]; then
      ports=1
    fi
  done < $i
  j=$((${#protocols}-1))
  if [ "${protocols:$j:1}" == "," ]; then
    protocols="${protocols::$j}]\""
  else
    protocols="$protocols]\""
  fi

  arr_protocol=(${protocols/,/ })
  shift;
  bar=$(printf ",%s" "${arr_protocol[@]}")
  bar=${bar:1}

  while read -r li; do
    if [ "$first" == "yes" ]; then
      echo "$li" > $path.new
      first="no"
    fi
    arr_li=(${li//,/ })
    if [ "${arr_li[1]}" == "${bar[0]}" ]; then
      echo "$li${bar[1]}" >> $path.new
      break
    fi
  done < $path
done

mv $path.new $path

cmd="cd /dns-data; git commit -a -m \"update dns records\";";
eval $cmd;

echo "done"
