FROM alpine:3.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    nmap \
    && rm -rf /var/cache/apk/*

CMD hostname --all-ip-addresses | \
    awk '{for(i=1;i<=NF;i++){printf "nmap -sS %s/24\n", $i};}' | \
    xargs -0 bash -c
