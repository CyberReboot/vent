FROM redis:5-alpine
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="redis" \
      vent.groups="core" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

HEALTHCHECK --interval=15s --timeout=15s \
 CMD redis-cli ping
CMD redis-server --appendonly yes
