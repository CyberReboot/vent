FROM alpine:3.11
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="ncapture" \
      vent.groups="collection,hidden,network,network_tap_child"

ENV BUILDDEPS="autoconf automake bison build-base flex gcc git libtool libpcap-dev libpcap linux-headers musl-dev python3-dev yaml-dev"
WORKDIR /tmp

# TODO: libwdcap currently requires openssl 1.0.2
RUN apk add --update $BUILDDEPS \
    bash \
    coreutils \
    python3 \
    && rm -rf /var/cache/apk/* \
    && mkdir /src \
    && cd /src \
    && git clone https://github.com/wanduow/wandio.git \
    && git clone https://github.com/LibtraceTeam/libtrace.git \
    && git clone https://github.com/openssl/openssl -b OpenSSL_1_0_2s \
    && git clone https://github.com/wanduow/libwdcap.git \
    && cd /src/wandio \
    && ./bootstrap.sh \
    && ./configure \
    && make && make install \
    && cd /src/libtrace \
    && ./bootstrap.sh \
    && ./configure \
    && make && make install \
    && cd /src/openssl \
    && ./config --prefix=/usr/local --openssldir=/usr/local/openssl \
    && make && make install \
    && cd /src/libwdcap \
    && ./bootstrap.sh \
    && ./configure --disable-shared \
    && make && make install \
    && cd examples \
    && g++ -fpermissive -o tracecapd tracecapd.c -L/usr/local/lib -Wl,-Bstatic -ltrace -lwdcap -Wl,-Bdynamic -lpcap -lssl -lcrypto -lwandio -lyaml \
    && cp tracecapd /usr/local/bin \
    && rm -rf /src \
    && apk del $BUILDDEPS \
    && apk add \
    libstdc++ \
    libgcc \
    libpcap \
    yaml

VOLUME /tmp
COPY . /tmp

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["/tmp/run.sh"]
