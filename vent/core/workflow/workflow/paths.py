import docker
import falcon
import json
import redis
import time

from vent.helpers.meta import Containers


class ConnectionnR(object):
    """
    This endpoint is for population connection data
    """
    def on_get(self, req, resp, from_conn, to_conn):
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_200
        r = None
        try:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
        except Exception as e:  # pragma: no cover
            try:
                r = redis.StrictRedis(host='localhost', port=6379, db=0)
            except Exception as e:  # pragma: no cover
                resp.body = "(False, 'unable to connect to redis because: " + str(e) + "')"
                return

        resp.body = "OK"
        return


class DataR(object):
    """
    This endpoint is for returning data.json
    """
    def get_nodes(self):
        nodes = [{
         'renderer': 'region',
         'name': 'VENT',
         'class': 'normal',
         'maxVolume': 1000,
         'updated': int(round(time.time() * 1000)),
         'nodes': [],
         'connections': []
        }]
        containers = Containers(exclude_labels=['monitoring'])
        for container in containers:
            node = {'renderer': 'focusedChild',
                    'name': container[0],
                    'class': 'normal'}
            nodes[0]['nodes'].append(node)
        return nodes

    def get_connections(self):
        # TODO, example data
        connections = [{"source": "cyberreboot-vent-rq-worker-master",
                        "target": "cyberreboot-crviz-master-HEAD",
                        "metrics": {"normal": 400,
                                    "danger": 99},
                        "notices": [],
                        "class": "normal"},
                       {"source": "cyberreboot-poseidon-api-master-HEAD",
                        "target": "cyberreboot-vent-file-drop-master",
                        "metrics": {"normal": 200,
                                    "danger": 99},
                        "notices": [],
                        "class": "normal"}]
        return connections

    def build_data(self):
        # generate json object for vizceral
        data = {}
        data['renderer'] = 'global'
        data['name'] = 'vent'
        data['nodes'] = []
        data['connections'] = []
        nodes = self.get_nodes()
        connections = self.get_connections()
        for node in nodes:
            data['nodes'].append(node)
        for connection in connections:
            data['nodes'][0]['connections'].append(connection)
        return data

    def on_get(self, req, resp):
        data = self.build_data()
        resp.body = json.dumps(data)
        resp.cache_control = ['no-cache', 'no-store', 'must-revalidate']
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_200
        return
