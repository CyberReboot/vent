FROM alpine:3.11
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="rq_dashboard" \
      vent.groups="monitoring" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update \
    curl \
    git \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

RUN pip3 install --no-cache-dir --upgrade pip==19.1

# healthcheck
COPY healthcheck /healthcheck
RUN pip3 install --no-cache-dir -r /healthcheck/requirements.txt
ENV FLASK_APP /healthcheck/hc.py
HEALTHCHECK --interval=15s --timeout=15s \
 CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1

# get newer for worker list fix
RUN pip3 install rq-dashboard==0.5.2

COPY rq_dash_settings.py /rq_dash_settings.py

COPY run.sh /run.sh
RUN chmod 755 /run.sh

EXPOSE 9181

CMD (flask run > /dev/null 2>&1) & (/run.sh)
