#!/usr/bin/env python
import ast
import datetime
import pika
import sys
import time
import uuid

from elasticsearch import Elasticsearch

es = None

def connections(wait):
    global es
    while wait:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            channel.exchange_declare(exchange='topic_recs', type='topic')

            result = channel.queue_declare(exclusive=True)
            queue_name = result.method.queue
            es = Elasticsearch(['elasticsearch'])
            wait = False
            print "connected to rabbitmq..."
        except Exception as e:
            print "waiting for connection to rabbitmq..."
            time.sleep(2)
            wait = True
    return channel, queue_name

def callback(ch, method, properties, body):
    # send to elasticsearch index
    index = "pcap"
    if method.routing_key.split(".")[0] == 'syslog':
        body = body.strip().replace('"', '\"')
        body = '{"log":"'+body+'"}'
        index = "syslog"
    elif method.routing_key.split(".")[0] == 'dshell_netflow':
        index = "dshell_netflow"
    elif method.routing_key.split(".")[0] == 'hex_flow':
        index = "hex_flow"
    try:
        doc = ast.literal_eval(body)
        res = es.index(index=index, doc_type=method.routing_key.split(".")[0], id=method.routing_key+"."+str(uuid.uuid4()), body=doc)
        print " [x] "+str(datetime.datetime.utcnow())+" UTC {0!r}:{1!r}".format(method.routing_key, body)
    except Exception as e:
        pass

if __name__ == "__main__": # pragma: no cover
    channel, queue_name = connections(True)

    binding_keys = sys.argv[1:]
    if not binding_keys:
        print >> sys.stderr, "Usage: {0!s} [binding_key]...".format(sys.argv[0])
        sys.exit(1)

    for binding_key in binding_keys:
        channel.queue_bind(exchange='topic_recs',
                           queue=queue_name,
                           routing_key=binding_key)

    print ' [*] Waiting for logs. To exit press CTRL+C'
    channel.basic_consume(callback,
                          queue=queue_name,
                          no_ack=True)
    channel.start_consuming()
