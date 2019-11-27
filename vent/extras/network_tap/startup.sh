#!/bin/sh
gunicorn -b :8080 -k gevent -w 4 --reload ncontrol.ncontrol
