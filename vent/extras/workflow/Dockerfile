FROM alpine:3.10
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="workflow" \
      vent.groups="files,monitoring,workflow" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update \
    curl \
    gcc \
    git \
    linux-headers \
    musl-dev \
    python3-dev \
    && rm -rf /var/cache/apk/*

RUN pip3 install --no-cache-dir --upgrade pip==19.1

# healthcheck
COPY healthcheck /healthcheck
RUN pip3 install --no-cache-dir -r /healthcheck/requirements.txt
ENV FLASK_APP /healthcheck/hc.py
HEALTHCHECK --interval=15s --timeout=15s \
 CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1

COPY requirements.txt /workflow/requirements.txt
WORKDIR /workflow
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /workflow

EXPOSE 8080

CMD (flask run > /dev/null 2>&1) & (gunicorn -b :8080 -k gevent -w 4 --reload workflow.workflow)
