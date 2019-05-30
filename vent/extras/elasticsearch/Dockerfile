FROM docker.elastic.co/elasticsearch/elasticsearch:7.1.1
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="elasticsearch" \
      vent.groups="search" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

HEALTHCHECK --interval=15s --timeout=15s \
  CMD curl --silent --fail http://localhost:9200/_cluster/health || exit 1
