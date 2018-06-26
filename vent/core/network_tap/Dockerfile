FROM python:3-alpine3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="network_tap" \
      vent.groups="core,collection,files,network" \
      vent.section="cyberreboot:vent:/vent/core/network_tap:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update \
    gcc \
    git \
    linux-headers \
    musl-dev \
    python3-dev \
    && rm -rf /var/cache/apk/*

RUN pip3 install --upgrade pip

# healthcheck
COPY healthcheck /healthcheck
RUN pip3 install -r /healthcheck/requirements.txt
ENV FLASK_APP /healthcheck/hc.py
HEALTHCHECK --interval=15s --timeout=15s \
 CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1

COPY . /network-tap
WORKDIR /network-tap
RUN pip3 install -r ncontrol/requirements.txt

EXPOSE 8080

CMD (flask run < /dev/null 2>&1) & (/network-tap/startup.sh)
