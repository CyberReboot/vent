FROM ubuntu:14.04.2
RUN apt-get update && apt-get install -y autoconf \
                                         gcc \
                                         git \
                                         libtool \
                                         libpcap-dev \
                                         make
RUN git clone https://github.com/ntop/nDPI.git
WORKDIR /nDPI
RUN ./autogen.sh
RUN ./configure
RUN make
RUN mv /nDPI/example/ndpiReader /usr/bin/ndpiReader

ENTRYPOINT ["/usr/bin/ndpiReader"]
CMD [""]
