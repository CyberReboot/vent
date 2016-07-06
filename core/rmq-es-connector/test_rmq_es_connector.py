import pytest

import rmq_es_connector

class Method():
    routing_key = None
    def __init__(self, routing_key=None):
        self.routing_key = routing_key

def test_rmq_es_connector_connections():
    """ tests the connections functions """
    rmq_es_connector.connections(False)

def test_rmq_es_connector_callback():
    """ tests the callback functions """
    rmq_es_connector.callback(None, None, None, None)
    rmq_es_connector.callback(None, None, None, [])
    method = Method(routing_key="syslog.foo")
    rmq_es_connector.callback(None, method, None, None)
    method = Method(routing_key="dshell_netflow.foo")
    rmq_es_connector.callback(None, method, None, None)
    method = Method(routing_key="hex_flow.foo")
    rmq_es_connector.callback(None, method, None, None)
