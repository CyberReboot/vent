# build stage
FROM golang:alpine AS builder
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
COPY main.go /app/main.go
WORKDIR /app
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o gonet .

# final stage
FROM scratch
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
COPY --from=builder /app/gonet /gonet
CMD ["/gonet"]

LABEL vent=""
