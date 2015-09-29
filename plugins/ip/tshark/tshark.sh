#!/bin/bash
PATH="$1"
/usr/bin/tshark -r $PATH -T fields -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport | /usr/bin/tee >(/usr/bin/sort | /usr/bin/uniq -c > /tmp/results.out) >(/usr/bin/wc -l > /tmp/count.out) > /dev/null
