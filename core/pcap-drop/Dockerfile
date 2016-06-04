FROM alpine:3.4
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    python \
    py-pip \
    && rm -rf /var/cache/apk/*

ADD . /pcap-drop
RUN pip install -r /pcap-drop/requirements.txt

WORKDIR /pcap-drop

ENTRYPOINT ["python", "/pcap-drop/pcap_drop.py"]

# volume dir to watch
# cmd specify dir
# CMD ["/data"]
