#!/bin/bash
PATH="$1"
/bin/cat $PATH | /bin/grep -v '^#' | /usr/bin/awk  -v OFS=',' '{print $3,$9}' | /usr/bin/tee >(/usr/bin/sort | /usr/bin/uniq -c > /tmp/results.out) >(/usr/bin/wc -l > /tmp/count.out) > /dev/null
