#!/bin/sh

# loop forever
# read in configuration of tools/settings
# spin up containers based on configurations
# periodically cleanup containers/images
# log everything to stdout
#curl the remote docker api on 172.
# curl -k --cert cert.pem --key key.pem https://172.17.42.1:2376/images/json
# echo -e "GET /images/json HTTP/1.0\r\n" | nc -U /var/run/docker.sock | awk 'NR>5' | jq '.'
# echo -e 'POST /containers/create HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 36\r\n\r\n{"Image":"ubuntu","Cmd":"/bin/bash"}' | nc -U /var/run/docker.sock

#docker run -it -v /mnt/sda1/var/lib/boot2docker/tls:/certs vent-management /bin/sh
