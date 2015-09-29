FROM ubuntu:14.04.2
RUN apt-get update && apt-get install -y libpcap-dev

ADD ndpiReader /usr/bin/ndpiReader

ENTRYPOINT ["/usr/bin/ndpiReader"]
CMD [""]
