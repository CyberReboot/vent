#!/bin/bash

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

#docker run -it -v /mnt/sda1/var/lib/boot2docker/tls:/certs -v /var/run/docker.sock:/var/run/docker.sock vent-management /bin/bash

unset n
sep='|'
while read -r line; do
  echo $line
  first=${line%%"$sep"*}
  rest=${line#*"$sep"}
  second=${rest%%"$sep"*}
  last=${rest#*"$sep"}
  echo
  echo "first: $first"
  echo
  echo "second: $second"
  echo
  echo "last: $last"
  echo
  : $[n++]
done < vent_start.txt
sed -i "1,$n d" vent_start.txt
