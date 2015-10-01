#!/bin/bash
PATH="$1"
/usr/bin/tshark -r $PATH -T fields -e ip.src -e dns.qry.name | /usr/bin/tee >(/usr/bin/sort | /usr/bin/uniq -c > /tmp/results.out) >(/usr/bin/wc -l > /tmp/count.out) > /dev/null
