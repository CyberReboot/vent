#!/usr/bin/env bash

# loop forever
# read in configuration of tools/settings
# spin up containers based on configurations
# log everything to stdout

start_containers() {

  n=0
  sep='|'
  while read -r line; do
    echo "reading...$line"
    # first is the image names and params to run them with
    container=${line%%"$sep"*}
    # rand is whether or not to add a random number at the end of the name
    rand=${line#*"$sep"}
    length=$(echo "$container" | jq -c -M '.[]' | wc -l)
    i=0
    while [ $i -lt $length ]; do
      name="echo '$container' | jq 'keys' | jq -M '.[$i]'"
      name=$(eval $name)
      p="echo '$container' | jq -c -M '.$name'"
      p=$(eval $p)

      # add random numbers to end of name
      name=${name:1:${#name}-2}
      if [ $rand = "1" ]; then
        name=$name$RANDOM
      fi

      # fix escapes, trues, falses, and nulls
      p=${p//\"false\"/false}
      p=${p//\"true\"/true}
      p=${p//\"null\"/null}
      p="${p//\"\{/\{}"
      p="${p//\}\"/\}}"
      p="${p//\"\[/\[}"
      p="${p//\]\"/\]}"
      p=$(echo "$p" | sed 's/\\//g')

      echo "checking if container already exists..."
      exists="echo -e 'GET /containers/json?all=1&filters={%22name%22:[%22$name%22]} HTTP/1.1\r\nHost: localhost\r\n'"
      container_id=$(eval $exists | nc -U /var/run/docker.sock | tail -n4 | head -n1 | jq '.[].Id' 2>/dev/null)
      if [ -z "$container_id" ]; then
        echo "doesn't exist, creating...$name: $p"
        one="echo -e 'POST /containers/create?name=$name HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: 1023\r\n\r\n$p'"
        container_id=$(eval $one | nc -U /var/run/docker.sock | tail -1 | jq '.Id')
      fi
      echo "starting...$container_id"
      /usr/local/bin/docker start ${container_id:1:${#container_id}-2} > /dev/null
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
