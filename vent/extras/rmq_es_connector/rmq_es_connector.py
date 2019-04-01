#!/usr/bin/env python
import json
import os
import sys
import time
import uuid

import pika
from elasticsearch import Elasticsearch


class RmqEs():
    """
    opens a connection to rabbitmq and receives messages based on the provided
    binding keys and then takes those messages and sends them to an
    elasticsearch index
    """
    es_conn = None
    es_host = None
    # get custom set port or else use default port
    es_port = int(os.getenv('ELASTICSEARCH_CUSTOM_PORT', 9200))
    rmq_host = None
    # get custom set port or else use default port
    rmq_port = int(os.getenv('RABBITMQ_CUSTOM_PORT', 5672))
    channel = None
    queue_name = None

    def __init__(self, es_host='elasticsearch', rmq_host='rabbitmq'):
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
                params = pika.ConnectionParameters(host=self.rmq_host,
                                                   port=self.rmq_port)
                connection = pika.BlockingConnection(params)
                self.channel = connection.channel()
                self.channel.exchange_declare(exchange='topic_recs',
                                              exchange_type='topic')

                result = self.channel.queue_declare()
                self.queue_name = result.method.queue
                self.es_conn = Elasticsearch([{'host': self.es_host,
                                               'port': self.es_port}])
                wait = False
                print('connected to rabbitmq and elasticsearch...')
            except Exception as e:  # pragma: no cover
                print(str(e))
                print('waiting for connection to rabbitmq...' + str(e))
                time.sleep(2)
                wait = True

    def callback(self, ch, method, properties, body):
        """
        callback triggered on rabiitmq message received and sends it to
        an elasticsearch index
        """
        index = method.routing_key.split('.')[1]
        index = index.replace('/', '-')
        failed = False
        body = str(body)
        try:
            doc = json.loads(body)
        except Exception as e:  # pragma: no cover
            try:
                body = body.strip().replace('"', '\"')
                body = '{"log":"' + body + '"}'
                doc = json.loads(body)
            except Exception as e:  # pragma: no cover
                failed = True

        if not failed:
            try:
                self.es_conn.index(index=index,
                                   doc_type=method.routing_key.split('.')[1],
                                   id=method.routing_key + '.' +
                                   str(uuid.uuid4()),
                                   body=doc)
            except Exception as e:  # pragma: no cover
                print('Failed to send document to elasticsearch because: ' + str(e))

    def start(self):
        """ start the channel listener and start consuming messages """
        self.connections(True)

        binding_keys = sys.argv[1:]
        if not binding_keys:
            print(sys.stderr,
                  'Usage: {0!s} [binding_key]...'.format(sys.argv[0]))
            sys.exit(0)

        for binding_key in binding_keys:
            self.channel.queue_bind(exchange='topic_recs',
                                    queue=self.queue_name,
                                    routing_key=binding_key)

    def consume(self):  # pragma: no cover
        """ start consuming rabbitmq messages """
        print(' [*] Waiting for logs. To exit press CTRL+C')
        self.channel.basic_consume(self.queue_name, self.callback)
        self.channel.start_consuming()


if __name__ == '__main__':  # pragma: no cover
    rmq_es = RmqEs()
    rmq_es.start()
    rmq_es.consume()
