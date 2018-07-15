import ast
import docker
import falcon
import json
import redis
import socket


class CreateR(object):
    """
    This endpoint is for creating a new filter
    """

    def on_post(self, req, resp):
        """
        Send a POST request with id/nic/interval/filter/iters and it will start
        a container for collection with those specifications
        """
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_200

        # verify payload is in the correct format
        # default to no filter
        payload = {}
        if req.content_length:
            try:
                payload = json.load(req.stream)
            except Exception as e:  # pragma: no cover
                resp.body = 'malformed payload'
                return
        else:
            resp.body = 'malformed payload'
            return

        if 'filter' not in payload:
            payload['filter'] = ''

        # payload should have the following fields:
        # - id
        # - nic
        # - interval
        # - filter
        # - iters
        # should spin up a tcpdump container that writes out pcap files based
        # on the filter needs to be attached to the nic specified, if iters is
        # -1 then loops until killed, otherwise completes iters number of
        # captures (and creates that many pcap files) should keep track of
        # container id, container name, and id of filter and filter + whatever
        # else is in payload in redis

        # verify payload has necessary information
        if 'nic' not in payload:
            resp.body = 'payload missing nic'
            return
        if 'id' not in payload:
            resp.body = 'payload missing id'
            return
        if 'interval' not in payload:
            resp.body = 'payload missing interval'
            return
        if 'iters' not in payload:
            resp.body = 'payload missing iters'
            return

        # connect to redis
        if 'metadata' in payload:
            r = None
            try:
                r = redis.StrictRedis(host='redis', port=6379, db=0)
            except Exception as e:  # pragma: no cover
                try:
                    r = redis.StrictRedis(host='localhost', port=6379, db=0)
                except Exception as e:  # pragma: no cover
                    resp.body = "(False, 'unable to connect to redis because: " + str(e) + "')"
                    return
            if r:
                metadata = {}
                try:
                    metadata = ast.literal_eval(payload['metadata'])
                except Exception as e:  # pragma: no cover
                    resp.body = "(False, 'unable to convert metadata [ " + str(payload['metadata']) + " ] into a dict because: " + str(e) + "')"
                    return
                try:
                    r.hmset(payload['id'], metadata)
                    r.hmset(metadata['endpoint_data']['ip-address'], {'poseidon_hash': payload['id']})
                    r.sadd('ip_addresses', metadata['endpoint_data']['ip-address'])
                except Exception as e:  # pragma: no cover
                    resp.body = "(False, 'unable to store contents of the payload [ " + str(metadata) + " ] in redis because: " + str(e) + "')"
                    return

        # connect to docker
        c = None
        try:
            c = docker.from_env()
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'unable to connect to docker because: " + str(e) + "')"
            return

        # spin up container with payload specifications
        if c:
            tool_d = {"network_mode": "host",
                      "volumes_from": [socket.gethostname()]}

            cmd = '/tmp/run.sh ' + payload['nic'] + ' ' + payload['interval']
            cmd += ' ' + payload['id'] + ' ' + payload['iters'] + ' '
            cmd += payload['filter']
            try:
                container_id = c.containers.run(image='cyberreboot/vent-ncapture:master',
                                                command=cmd, detach=True, **tool_d)
            except Exception as e:  # pragma: no cover
                resp.body = "(False, 'unable to start container because: " + str(e) + "')"
                return

        resp.body = "(True, 'successfully created and started filter: " + str(payload['id']) + " on container: " + str(container_id) + "')"
        return


class DeleteR(object):
    """
    This endpoint is for deleting a network tap filter container
    """

    def on_post(self, req, resp):
        """
        Send a POST request with a docker container ID and it will be deleted.

        Example input: {'id': "12345"}, {'id': ["123", "456"]}
        """
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_200

        # verify user input
        payload = {}
        if req.content_length:
            try:
                payload = json.load(req.stream)
            except Exception as e:  # pragma: no cover
                resp.body = 'malformed payload'
                return
        else:
            resp.body = 'malformed payload'
            return

        # verify payload has a container ID
        if 'id' not in payload:
            resp.body = 'payload missing id'
            return

        # connect to docker and stop the given container
        c = None
        try:
            c = docker.from_env()
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'unable to connect to docker because: " + str(e) + "')"
            return

        # delete containers chosen from CLI
        try:
            for container_id in payload['id']:
                c.containers.get(container_id).remove()
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'unable to delete containers because: " + str(e) + "')"
            return

        resp.body = "(True, 'container successfully deleted: " + str(payload['id']) + "')"
        return


class InfoR(object):
    """
    This endpoint is for returning info about this service
    """

    def on_get(self, req, resp):
        resp.body = json.dumps({'version': 'v0.1.0'})
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_200
        return


class ListR(object):
    """
    This endpoint is for listing all filter containers
    """

    def on_get(self, req, resp):
        """
        Send a GET request to get the list of all of the filter containers
        """
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_200

        # connect to docker
        try:
            containers = docker.from_env()
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'unable to connect to docker because: " + str(e) + "')"
            return

        # search for all docker containers and grab ncapture containers
        container_list = []
        try:
            for c in containers.containers.list(all=True):
                # TODO: maybe find a way to not have to hard code image name
                if c.attrs["Config"]["Image"] == \
                        "cyberreboot/vent-ncapture:master":
                    # the core container is not what we want
                    if "core" not in c.attrs["Config"]["Labels"]\
                       ["vent.groups"]:
                        lst = {}
                        lst['id'] = c.attrs["Id"][:12]
                        lst['status'] = c.attrs["State"]["Status"]
                        lst['args'] = c.attrs['Args']
                        container_list.append(lst)
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'Failure because: " + str(e) + "')"
            return

        resp.body = json.dumps(container_list)
        return


class NICsR(object):
    """
    This endpoint is for listing all available network interfaces
    """

    def on_get(self, req, resp):
        """
        Send a GET request to get the list of all available network interfaces
        """
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_200

        # connect to docker
        try:
            d_client = docker.from_env()
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'unable to connect to docker because: " + str(e) + "')"
            return

        # start container to get network interfaces
        nics = ""
        try:
            nics = d_client.containers.run('cyberreboot/gonet',
                                           network_mode='host')
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'Failure because: " + str(e) + "')"
            return

        resp.body = nics
        return


class StartR(object):
    """
    This endpoint is for starting a network tap filter container
    """

    def on_post(self, req, resp):
        """
        Send a POST request with a docker container ID and it will be started.

        Example input: {'id': "12345"}, {'id': ["123", "456"]}
        """
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_200

        # verify user input
        payload = {}
        if req.content_length:
            try:
                payload = json.load(req.stream)
            except Exception as e:  # pragma: no cover
                resp.body = 'malformed payload'
                return
        else:
            resp.body = 'malformed payload'
            return

        # verify payload has a container ID
        if 'id' not in payload:
            resp.body = "(False, 'payload missing container id')"
            return

        # connect to docker and stop the given container
        c = None
        try:
            c = docker.from_env()
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'unable to connect to docker because: " + str(e) + "')"
            return

        # start containers chosen from CLI
        try:
            for container_id in payload['id']:
                c.containers.get(container_id).start()
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'unable to start list of containers because: " + str(e) + "')"
            return

        resp.body = "(True, 'container successfully started: " + str(payload['id']) + "')"
        return


class StopR(object):
    """
    This endpoint is for stopping a network tap filter container
    """

    def on_post(self, req, resp):
        """
        Send a POST request with a docker container ID and it will be stopped.

        Example input: {'id': "12345"}, {'id': ["123", "456"]
        """
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_200

        # verify user input
        payload = {}
        if req.content_length:
            try:
                payload = json.load(req.stream)
            except Exception as e:  # pragma: no cover
                resp.body = 'malformed payload'
                return
        else:
            resp.body = 'malformed payload'
            return

        # verify payload has a container ID
        if 'id' not in payload:
            resp.body = "(False, 'payload missing container id')"
            return

        # connect to docker and stop the given container
        c = None
        try:
            c = docker.from_env()
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'unable to connect to docker because: " + str(e) + "')"
            return

        # stop containers chosen from CLI
        try:
            for container_id in payload['id']:
                c.containers.get(container_id).stop()
        except Exception as e:  # pragma: no cover
            resp.body = "(False, 'unable to stop list of containers because: " + str(e) + "')"
            return

        resp.body = "(True, 'container successfully stopped: " + str(payload['id']) + "')"
        return


class UpdateR(object):
    """
    This endpoint is for updating a filter
    """

    def on_post(self, req, resp):
        """
        Send a POST request with id and metadata and it will update the
        existing filter metadata with those specifications
        """
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_200

        # verify payload is in the correct format
        payload = {}
        if req.content_length:
            try:
                payload = json.load(req.stream)
            except Exception as e:  # pragma: no cover
                resp.body = 'malformed payload'
                return
        else:
            resp.body = 'malformed payload'
            return

        # payload should have the following fields:
        # - id
        # - metadata

        # verify payload has necessary information
        if 'id' not in payload:
            resp.body = 'payload missing id'
            return
        if 'metadata' not in payload:
            resp.body = 'payload missing metadata'
            return

        # connect to redis
        r = None
        try:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
        except Exception as e:  # pragma: no cover
            try:
                r = redis.StrictRedis(host='localhost', port=6379, db=0)
            except Exception as e:  # pragma: no cover
                resp.body = "(False, 'unable to connect to redis because: " + str(e) + "')"
                return
        if r:
            metadata = {}
            try:
                metadata = ast.literal_eval(payload['metadata'])
            except Exception as e:  # pragma: no cover
                resp.body = "(False, 'unable to convert metadata [ " + str(payload['metadata']) + " ] into a dict because: " + str(e) + "')"
                return
            try:
                r.hmset(payload['id'], metadata)
                r.hmset(metadata['endpoint_data']['ip-address'], {'poseidon_hash': payload['id']})
                r.sadd('ip_addresses', metadata['endpoint_data']['ip-address'])
            except Exception as e:  # pragma: no cover
                resp.body = "(False, 'unable to store contents of the payload [ " + str(metadata) + " ] in redis because: " + str(e) + "')"
                return

        resp.body = "(True, 'successfully updated filter: " + str(payload['id']) + "')"
        return
