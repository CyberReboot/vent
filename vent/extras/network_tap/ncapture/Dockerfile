FROM alpine:3.10
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="ncapture" \
      vent.groups="collection,hidden,network,network_tap_child"
RUN apk add --update \
    bash \
    bison \
    build-base \
    flex \
    gcc \
    git \
    linux-headers \
    musl-dev \
    && rm -rf /var/cache/apk/* \
    && mkdir /src \
    && cd /src \
    && git clone https://github.com/the-tcpdump-group/libpcap.git \
    && git clone https://github.com/cglewis/tcpdump.git \
    && cd /src/libpcap \
    && ./configure \
    && make && make install \
    && cd /src/tcpdump \
    && git fetch origin && git checkout send-upstream \
    && ./configure \
    && make && make install \
    && rm -rf /src \
    && apk del \
    bison \
    build-base \
    flex \
    gcc \
    git \
    linux-headers \
    musl-dev

VOLUME /tmp
WORKDIR /tmp
COPY run.sh run.sh

CMD ["/tmp/run.sh"]
