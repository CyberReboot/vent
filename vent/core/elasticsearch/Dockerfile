FROM docker.elastic.co/elasticsearch/elasticsearch:6.6.0
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="elasticsearch" \
      vent.groups="core,search" \
      vent.section="cyberreboot:vent:/vent/core/elasticsearch:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

HEALTHCHECK --interval=15s --timeout=15s \
  CMD curl --silent --fail http://localhost:9200/_cluster/health || exit 1
