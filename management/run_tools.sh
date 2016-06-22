#!/usr/bin/env bash

# loop forever
# read in configuration of tools/settings
# spin up containers based on configurations
# log everything to stdout

start_containers() {

  n=0
  sep='|'
  while read -r line; do
    echo $line
    first=${line%%"$sep"*}
    rest=${line#*"$sep"}
    second=${rest%%"$sep"*}
    rest=${rest#*"$sep"}
    third=${rest%%"$sep"*}
    rest=${rest#*"$sep"}
    forth=${rest%%"$sep"*}
    rest=${rest#*"$sep"}
    last=${rest%%"$sep"*}
    rand=${rest#*"$sep"}
    # first is name of mode/profile/type
    # second is schedule for the mode/profile/type
    # third is the image names and params for core
    # forth is the image names and params to run them with
    # last is the delay dict
    length=$(echo "$forth" | jq -c -M '.[]' | wc -l)
    i=0
    while [ $i -lt $length ]; do
      name="echo '$forth' | jq 'keys' | jq -M '.[$i]'"
      name=$(eval $name)
      p="echo '$forth' | jq -c -M '.$name'"
      p=$(eval $p)
      name=${name:1:${#name}-2}
      if [ $rand = "1" ]; then
        name=$name$RANDOM
      fi
      p=${p//\"false\"/false}
      p=${p//\"true\"/true}
      p=${p//\"null\"/null}
      p="${p//\"\{/\{}"
      p="${p//\}\"/\}}"
      p="${p//\"\[/\[}"
      p="${p//\]\"/\]}"
      p=$(echo "$p" | sed 's/\\//g')
      echo "$name: $p"
      exists="echo -e 'GET /containers/json?all=1&filters={%22name%22:[%22$name%22]} HTTP/1.0\r\n\r\n'"
      container_id=$(eval $exists | nc -U /var/run/docker.sock | tail -1 | jq '.[].Id')
      if [ -z "$container_id" ]; then
        one="echo -e 'POST /containers/create?name=$name HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 1023\r\n\r\n$p'"
        container_id=$(eval $one | nc -U /var/run/docker.sock | tail -1 | jq '.Id')
      fi
      echo "$container_id"
      two="echo -e \"POST /containers/${container_id:1:${#container_id}-2}/start HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n{}'\" | nc -U /var/run/docker.sock"
      eval $two
      : $[i++]
    done

    length=$(echo "$third" | jq -c -M '.[]' | wc -l)
    i=0
    while [ $i -lt $length ]; do
      name="echo '$third' | jq 'keys' | jq -M '.[$i]'"
      name=$(eval $name)
      p="echo '$third' | jq -c -M '.$name'"
      p=$(eval $p)
      name=${name:1:${#name}-2}
      p=${p//\"false\"/false}
      p=${p//\"true\"/true}
      p=${p//\"null\"/null}
      p="${p//\"\{/\{}"
      p="${p//\}\"/\}}"
      p="${p//\"\[/\[}"
      p="${p//\]\"/\]}"
      p=$(echo "$p" | sed 's/\\//g')
      echo "$name: $p"
      exists="echo -e 'GET /containers/json?all=1&filters={%22name%22:[%22$name%22]} HTTP/1.0\r\n\r\n'"
      container_id=$(eval $exists | nc -U /var/run/docker.sock | tail -1 | jq '.[].Id')
      if [ -z "$container_id" ]; then
        one="echo -e 'POST /containers/create?name=$name HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 1023\r\n\r\n$p'"
        container_id=$(eval $one | nc -U /var/run/docker.sock | tail -1 | jq '.Id')
      fi
      echo "$container_id"
      two="echo -e \"POST /containers/${container_id:1:${#container_id}-2}/start HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n{}'\" | nc -U /var/run/docker.sock"
      eval $two
      : $[i++]
    done
    : $[n++]
  done < /tmp/vent_start.txt

  if [ $n -gt 0 ]; then
    sed -i "1,$n d" /tmp/vent_start.txt
  fi

}

while true; do
  if [ -f "/tmp/vent_start.txt" ]; then
    start_containers
  fi
  sleep 1
done
