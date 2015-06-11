FROM ubuntu:14.04.2
MAINTAINER Charlie Lewis <clewis@iqt.org>
RUN apt-get update && apt-get install -y wget
RUN wget -O/etc/apt/sources.list.d/couchbase.list http://packages.couchbase.com/ubuntu/couchbase-ubuntu1204.list
RUN wget -O- http://packages.couchbase.com/ubuntu/couchbase.key | sudo apt-key add -
RUN apt-get update && apt-get install -y build-essential \
                                         curl \
                                         gcc \
                                         git \
                                         libcouchbase2 \
                                         libcouchbase-dev \
                                         openssl \
                                         python-dev \
                                         python-setuptools \
                                         python-software-properties \
                                         software-properties-common
RUN easy_install pip

# internal
RUN cd /tmp && curl -k -O https://github.com/raw/IT/pki/master/bin/local-ca.sh
RUN bash /tmp/local-ca.sh
RUN git clone https://github.com/CyberReboot/pinecone-aggregator.git

WORKDIR /pinecone-aggregator
RUN pip install -r /pinecone-aggregator/requirements.txt

ENTRYPOINT ["/usr/bin/python", "/pinecone-aggregator/pinecone-aggregator.py"]

# volume to dir to watch
# cmd specify dir and database
CMD [""]
