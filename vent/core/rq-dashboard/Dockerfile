FROM alpine:3.6
MAINTAINER Charlie Lewis <clewis@iqt.org>

RUN apk add --update \
    git \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

# get newer for worker list fix
RUN pip install git+https://github.com/mredar/rq-dashboard.git

COPY rq_dash_settings.py /rq_dash_settings.py

COPY run.sh /run.sh
RUN chmod 755 /run.sh

EXPOSE 9181

LABEL vent="" \
      vent.name="rq-dashboard" \
      vent.groups="core"

CMD ["/run.sh"]
