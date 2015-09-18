#!/usr/bin/env python
import datetime
import pika
import sys
import time

from elasticsearch import Elasticsearch

wait = True
while wait:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='rabbitmq'))
        channel = connection.channel()
        channel.exchange_declare(exchange='topic_recs',
                                 type='topic')

        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        wait = False
        print "connected to rabbitmq..."
    except:
        print "waiting for connection to rabbitmq..."
        time.sleep(2)
        wait = True

binding_keys = sys.argv[1:]
if not binding_keys:
    print >> sys.stderr, "Usage: %s [binding_key]..." % (sys.argv[0],)
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(exchange='topic_recs',
                       queue=queue_name,
                       routing_key=binding_key)

print ' [*] Waiting for logs. To exit press CTRL+C'

def callback(ch, method, properties, body):
    # !! TODO send to elasticsearch index
    print " [x] "+str(datetime.datetime.utcnow())+" UTC %r:%r" % (method.routing_key, body,)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
