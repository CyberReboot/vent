FROM alpine:3.6
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    python \
    py-pip \
    && rm -rf /var/cache/apk/*

COPY . /network-tap
WORKDIR /network-tap/ncontrol
RUN pip install -r requirements.txt

EXPOSE 8080

LABEL vent="" \
      vent.name="network-tap" \
      vent.groups="core,collection,files,network"

ENTRYPOINT ["python", "ncontrol.py"]
CMD [""]
