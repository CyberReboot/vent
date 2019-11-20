FROM alpine:3.10
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="ncapture" \
      vent.groups="collection,hidden,network,network_tap_child"
# TODO: remove custom libcap/tcpdump when cut over to tracepcapd
# tracepcapd is built first before tcpdump.
RUN apk add --update \
    autoconf \
    automake \
    bash \
    bison \
    build-base \
    flex \
    gcc \
    git \
    libtool \
    libpcap-dev \
    linux-headers \
    musl-dev \
    && rm -rf /var/cache/apk/* \
    && mkdir /src \
    && cd /src \
    && git clone https://github.com/the-tcpdump-group/libpcap.git \
    && git clone https://github.com/cglewis/tcpdump.git \
    && git clone https://github.com/wanduow/wandio.git \
    && git clone https://github.com/LibtraceTeam/libtrace.git \
    && git clone https://github.com/wanduow/libwdcap.git \
    && cd /src/wandio \
    && ./bootstrap.sh \
    && ./configure \
    && make && make install \
    && cd /src/libtrace \
    && ./bootstrap.sh \
    && ./configure \
    && make && make install \
    && apk del libpcap-dev libpcap \
    && cd /src/libwdcap \
    && ./bootstrap.sh \
    && ./configure \
    && make && make install \
    && cd examples \
    && gcc -o tracecapd tracecapd.c -ltrace -lwdcap \
    && cp tracecapd /usr/local/bin \
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
