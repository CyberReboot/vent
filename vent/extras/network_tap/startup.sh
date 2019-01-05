#!/bin/sh
python3 /network-tap/ncontrol/prestart.py
gunicorn -b :8080 -k gevent -w 4 --reload ncontrol.ncontrol
