#!/bin/sh

if [ -n "$SSH_ORIGINAL_COMMAND" ]; then
    exec /bin/sh -c "$SSH_ORIGINAL_COMMAND"
else
    docker rm vent-management; sudo /data/custom
    TERM=xterm LANG=C.UTF-8 /usr/local/bin/python2.7 /data/menu_launcher.py
fi
