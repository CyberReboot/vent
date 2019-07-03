FROM alpine:3.10
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"

RUN apk --no-cache add --update \
    curl \
    git \
    python3 \
    py3-pip && \
    pip3 install --no-cache-dir --upgrade pip==19.1

# healthcheck
COPY healthcheck /healthcheck
RUN pip3 install --no-cache-dir -r /healthcheck/requirements.txt
ENV FLASK_APP /healthcheck/hc.py
HEALTHCHECK --interval=15s --timeout=15s \
 CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1

COPY . /vent
RUN pip3 install --no-cache-dir /vent

RUN mkdir /root/.vent
VOLUME ["/root/.vent"]

ENV VENT_CONTAINERIZED true

CMD (flask run > /dev/null 2>&1) & (vent)
