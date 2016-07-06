import pytest

import rmq_es_connector

class Method():
    """ create mock method object """
    routing_key = None
    def __init__(self, routing_key=""):
        self.routing_key = routing_key

def test_rmq_es_connector_connections():
    """ tests the connections function """
    rmq_es = rmq_es_connector.RmqEs()
    rmq_es.connections(False)

def test_rmq_es_connector_callback():
    """ tests the callback function """
    rmq_es = rmq_es_connector.RmqEs()
    method = Method()
    rmq_es.callback(None, method, None, "[]")
    rmq_es.callback(None, method, None, "[]")
    method = Method(routing_key="syslog.foo")
    rmq_es.callback(None, method, None, "[]")
    method = Method(routing_key="dshell_netflow.foo")
    rmq_es.callback(None, method, None, "[]")
    method = Method(routing_key="hex_flow.foo")
    rmq_es.callback(None, method, None, "[]")

# TODO
# not testing `start` since it will be an infinite loop
