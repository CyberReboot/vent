FROM rabbitmq:3-management-alpine
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="rabbitmq" \
      vent.groups="core,messages,syslog" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update curl && rm -rf /var/cache/apk/*

HEALTHCHECK --interval=15s --timeout=15s \
  CMD curl --silent --fail http://localhost:15672/ || exit 1
