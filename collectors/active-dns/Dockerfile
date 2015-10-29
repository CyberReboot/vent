FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y dnsutils git zip
ADD . /dns

WORKDIR /dns
VOLUME /active-dns-data

ENTRYPOINT ["./list-servers.pl"]
CMD ["-h"]
