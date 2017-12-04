FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="rq_dashboard" \
      vent.groups="core" \
      vent.section="cyberreboot:vent:/vent/core/rq_dashboard:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update \
    git \
    python \
    py2-pip \
    && rm -rf /var/cache/apk/*

# get newer for worker list fix
RUN pip install git+https://github.com/mredar/rq-dashboard.git@bb5c8f93be5f1ac265bddd5d29fb98cf17fb2585

COPY rq_dash_settings.py /rq_dash_settings.py

COPY run.sh /run.sh
RUN chmod 755 /run.sh

EXPOSE 9181

CMD ["/run.sh"]
