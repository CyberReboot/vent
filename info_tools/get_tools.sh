#!/bin/sh
docker ps | grep 'ip/\|domain/\|mac/\|stats/\|hash/' | wc -l
