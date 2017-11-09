FROM elasticsearch:2-alpine
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="elasticsearch" \
      vent.groups="core,search" \
      vent.section="cyberreboot:vent:/vent/core/elasticsearch:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN plugin install mobz/elasticsearch-head
