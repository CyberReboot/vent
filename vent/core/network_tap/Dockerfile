FROM alpine:3.6
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"

RUN apk add --update \
    python \
    py-pip \
    && rm -rf /var/cache/apk/*

COPY . /network-tap
WORKDIR /network-tap/ncontrol
RUN pip install -r requirements.txt

EXPOSE 8080

LABEL vent="" \
      vent.name="network_tap" \
      vent.groups="core,collection,files,network" \
      vent.section="cyberreboot:vent:/vent/core/network_tap:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

ENTRYPOINT ["python", "ncontrol.py"]
CMD [""]
