#!/bin/sh
for worker in $(docker ps | grep core-rq-worker | awk '{print $12}')
do
    $(docker logs $worker 2>$worker.log)
    cat $worker.log | grep default:
done
