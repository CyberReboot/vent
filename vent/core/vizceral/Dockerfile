FROM node:alpine
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="vizceral" \
      vent.groups="core,monitoring,visualization,workflow" \
      vent.section="cyberreboot:vent:/vent/core/vizceral:master:HEAD" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

WORKDIR /usr/src/app
COPY package.json .

RUN npm install
COPY . .

EXPOSE 8080
CMD [ "npm", "run", "dev" ]
