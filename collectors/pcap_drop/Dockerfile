FROM ubuntu:14.04.2
# TODO consider using alpine instead
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apt-get update && apt-get install -y build-essential \
                                         python-dev \
                                         python-setuptools \
                                         python-software-properties \
                                         software-properties-common
RUN easy_install pip
ADD . /collector
RUN pip install -r /pcap_drop/requirements.txt

WORKDIR /pcap_drop

ENTRYPOINT ["/usr/bin/python", "/pcap_drop/pcap_drop.py"]

# volume dir to watch
# cmd specify dir
# CMD ["/data"]
