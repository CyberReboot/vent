FROM node:alpine
LABEL maintainer="Charlie Lewis <clewis@iqt.org>" \
      vent="" \
      vent.name="vizceral" \
      vent.groups="monitoring,visualization,workflow" \
      vent.repo="https://github.com/cyberreboot/vent" \
      vent.type="repository"

RUN apk add --update \
    curl \
    && rm -rf /var/cache/apk/*

WORKDIR /usr/src/app
COPY package.json .

RUN npm install
COPY . .

HEALTHCHECK --interval=15s --timeout=15s \
 CMD curl --silent --fail http://localhost:8080/ || exit 1

EXPOSE 8080
CMD [ "npm", "run", "dev" ]
