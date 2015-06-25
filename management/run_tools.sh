#!/usr/bin/env bash

# loop forever
# read in configuration of tools/settings
# spin up containers based on configurations
# periodically cleanup containers/images
# log everything to stdout
#curl the remote docker api on 172.
# curl -k --cert cert.pem --key key.pem https://172.17.42.1:2376/images/json
# echo -e "GET /images/json HTTP/1.0\r\n" | nc -U /var/run/docker.sock | awk 'NR>5' | jq '.'
# echo -e 'POST /containers/create?name=foo HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n{"Image":"ubuntu","Cmd":"/bin/bash"}' | nc -U /var/run/docker.sock
#POST /containers/(id)/start

# container_id=$(echo -e 'POST /containers/create?name=foo HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n{"Image":"redis"}' | nc -U /var/run/docker.sock | tail -1 | jq '.Id') && echo -e "POST /containers/${container_id:1:${#container_id}-2}/start HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n{}'" | nc -U /var/run/docker.sock

#docker run -it -v /mnt/sda1/var/lib/boot2docker/tls:/certs -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp vent-management /bin/bash

#container_id=$(echo -e 'POST /containers/create?name=foo HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n' | nc -U /var/run/docker.sock | tail -1 | jq '.Id') && echo -e "POST /containers/${container_id:1:${#container_id}-2}/start HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n{}'" | nc -U /var/run/docker.sock

start_containers() {

  n=0
  sep='|'
  while read -r line; do
    echo $line
    first=${line%%"$sep"*}
    rest=${line#*"$sep"}
    second=${rest%%"$sep"*}
    last=${rest#*"$sep"}
    # first is name of mode/profile/type
    # second is schedule for the mode/profile/type
    # last is the image names and params to run them with
    length=$(echo "$last" | jq -c -M '.[]' | wc -l)
    i=0
    while [ $i -lt $length ]; do
      name="echo '$last' | jq 'keys' | jq -M '.[$i]'"
      name=$(eval $name)
      p="echo '$last' | jq -c -M '.$name'"
      p=$(eval $p)
      name=${name:1:${#name}-2}
      echo "$name: $p"
      one="echo -e 'POST /containers/create?name=$name HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 1023\r\n\r\n$p'"
      container_id=$(eval $one | nc -U /var/run/docker.sock | tail -1 | jq '.Id')
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

stop_containers() {
  echo
}

status_containers() {
  echo
}

while true; do
  if [ -f "/tmp/vent_start.txt" ]; then
    start_containers
  fi
  if [ -f "/tmp/vent_stop.txt" ]; then
    stop_containers
  fi
  if [ -f "/tmp/vent_status.txt" ]; then
    status_containers
  fi
  sleep 1
done
