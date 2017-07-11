#!/bin/sh

if [ -n "$SSH_ORIGINAL_COMMAND" ]; then
    exec /bin/sh -c "$SSH_ORIGINAL_COMMAND"
else
    TERM=xterm vent
fi
