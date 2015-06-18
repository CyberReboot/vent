FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>
RUN apt-get update && apt-get install -y git \
                                         python-dev \
                                         python-setuptools
RUN easy_install pip

RUN git config --global http.sslVerify "false"
RUN git clone https://github.com/CyberReboot/honeycomb.git
RUN git clone https://github.com/CyberReboot/network-data.git
RUN pip install -r /honeycomb/requirements.txt

WORKDIR /honeycomb
VOLUME /honeycomb
EXPOSE 8080

ENTRYPOINT ["/usr/bin/env", "python"]
CMD ["honeycomb.py"]

