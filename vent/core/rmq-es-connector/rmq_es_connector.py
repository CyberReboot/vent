#!/usr/bin/env python
import ast
import datetime
import pika
import sys
import time
import uuid

from elasticsearch import Elasticsearch

class RmqEs():
    """
    opens a connection to rabbitmq and receives messages based on the provided
    binding keys and then takes those messages and sends them to an
    elasticsearch index
    """
    es_conn = None
    es_host = None
    rmq_host = None
    channel = None
    queue_name = None

    def __init__(self, es_host="elasticsearch", rmq_host="rabbitmq"):
        """ initialize host information """
        self.es_host = es_host
        self.rmq_host = rmq_host

    def connections(self, wait):
        """
        wait for connections to both rabbitmq and elasticsearch to be made
        before binding a routing key to a channel and sending messages to
        elasticsearch
        """
        while wait:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rmq_host))
                self.channel = connection.channel()
                self.channel.exchange_declare(exchange='topic_recs', type='topic')

                result = self.channel.queue_declare(exclusive=True)
                self.queue_name = result.method.queue
                self.es_conn = Elasticsearch([self.es_host])
                wait = False
                print("connected to rabbitmq...")
            except Exception as e:
                print("waiting for connection to rabbitmq...")
                time.sleep(2)
                wait = True

    def callback(self, ch, method, properties, body):
        """
        callback triggered on rabiitmq message received and sends it to
        an elasticsearch index
        """
        # !! TODO index needs to be reworked for multiple file types
        index = method.routing_key.split(".")[0]
        if method.routing_key.split(".")[0] == 'syslog':
            body = body.strip().replace('"', '\"')
            body = '{"log":"'+body+'"}'
        try:
            doc = ast.literal_eval(body)
            res = self.es_conn.index(index=index, doc_type=method.routing_key.split(".")[0], id=method.routing_key+"."+str(uuid.uuid4()), body=doc)
            print(" [x] "+str(datetime.datetime.utcnow())+" UTC {0!r}:{1!r}".format(method.routing_key, body))
        except Exception as e:
            pass

    def start(self):
        """ start the channel listener and start consuming messages """
        self.connections(True)

        binding_keys = sys.argv[1:]
        if not binding_keys:
            print(sys.stderr, "Usage: {0!s} [binding_key]...".format(sys.argv[0]))
            sys.exit(0)

        for binding_key in binding_keys:
            self.channel.queue_bind(exchange='topic_recs',
                                    queue=self.queue_name,
                                    routing_key=binding_key)

    def consume(self): # pragma: no cover
        """ start consuming rabbitmq messages """
        print(' [*] Waiting for logs. To exit press CTRL+C')
        self.channel.basic_consume(self.callback,
                              queue=self.queue_name,
                              no_ack=True)
        self.channel.start_consuming()

if __name__ == "__main__": # pragma: no cover
    rmq_es = RmqEs()
    rmq_es.start()
    rmq_es.consume()
