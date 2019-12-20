FROM alpine:3.11
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="network_tap" \
      vent.groups="files,network" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

COPY ncontrol/requirements.txt requirements.txt
COPY healthcheck /healthcheck

RUN apk add --update \
    curl \
    gcc \
    git \
    linux-headers \
    musl-dev \
    python3 \
    python3-dev \
    && pip3 install --no-cache-dir --upgrade pip==19.1 \
    && pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir -r /healthcheck/requirements.txt \
    && apk del \
    gcc \
    git \
    linux-headers \
    musl-dev \
    python3-dev \
    && rm -rf /var/cache/apk/*

# healthcheck
ENV FLASK_APP /healthcheck/hc.py
HEALTHCHECK --interval=15s --timeout=15s \
 CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1

COPY . /network-tap
WORKDIR /network-tap

EXPOSE 8080

CMD (flask run > /dev/null 2>&1) & (/network-tap/startup.sh)
