FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y nmap

CMD hostname --all-ip-addresses | \
    awk '{for(i=1;i<=NF;i++){printf "nmap -sS %s/24\n", $i};}' | \
    xargs -0 bash -c
