FROM python:3-alpine3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="workflow" \
      vent.groups="core,files,monitoring,workflow" \
      vent.section="cyberreboot:vent:/vent/core/workflow:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update \
    gcc \
    git \
    linux-headers \
    musl-dev \
    python3-dev \
    && rm -rf /var/cache/apk/*

COPY requirements.txt /workflow/requirements.txt
WORKDIR /workflow
RUN pip3 install -r requirements.txt

COPY . /workflow

EXPOSE 8080

CMD gunicorn -b :8080 -k gevent -w 4 --reload workflow.workflow
