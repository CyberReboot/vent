FROM alpine:3.7
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="file_drop" \
      vent.groups="core,files" \
      vent.section="cyberreboot:vent:/vent/core/file_drop:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

RUN pip3 install --upgrade pip

# healthcheck
COPY healthcheck /healthcheck
RUN pip3 install -r /healthcheck/requirements.txt
ENV FLASK_APP /healthcheck/hc.py
HEALTHCHECK --interval=15s --timeout=15s \
 CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1

COPY . /file-drop
RUN pip3 install -r /file-drop/requirements.txt

WORKDIR /file-drop

CMD (flask run > /dev/null 2>&1) & (python3 /file-drop/file_drop.py)
