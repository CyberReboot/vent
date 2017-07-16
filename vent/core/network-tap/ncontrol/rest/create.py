import ast
import docker
import redis
import socket
import web
import uuid


class CreateR:
    """
    This endpoint is for creating a new filter
    """

    @staticmethod
    def POST():
        """
        Send a POST request with id/nic/interval/filter/iters and it will start
        a container for collection with those specifications
        """
        web.header('Content-Type', 'application/json')

        # verify payload is in the correct format
        data = web.data()
        payload = {}
        try:
            payload = ast.literal_eval(data)
        except Exception as e:
            # !! TODO parse out url parms...
            return 'malformed payload: ' + str(e)

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
            return 'payload missing nic'
        if 'id' not in payload:
            return 'payload missing id'
        if 'interval' not in payload:
            return 'payload missing interval'
        if 'filter' not in payload:
            return 'payload missing filter'
        if 'iters' not in payload:
            return 'payload missing iters'

        # connect to redis
        r = None
        try:
            r = redis.StrictRedis(host='redis', port=6379, db=0)
        except Exception as e:
            return 'unable to connect to redis because: ' + str(e)

        # connect to docker
        c = None
        try:
            c = docker.from_env()
        except Exception as e:
            return 'unable to connect to docker because: ' + str(e)

        # store payload in redis
        if r:
            uid = str(uuid.uuid4())
            # !! TODO

        # spin up container with payload specifications
        if c:
            # TODO read from template
            tool_d = {"auto_remove": True,
                      "network_mode": "host",
                      "volumes_from": [socket.gethostname()]}

            cmd = '/tmp/run.sh ' + payload['nic'] + ' ' + payload['interval']
            cmd += ' ' + payload['id'] + ' ' + payload['iters'] + ' '
            cmd += payload['filter']
            try:
                container_id = c.containers.run(image='cyberreboot/vent-ncapture:master',
                                                command=cmd, detach=True, **tool_d)
            except Exception as e:
                return 'unable to start container because: ' + str(e)

        return ('successfully created and started filter ' +
                str(payload['id']) + ' on container: ' + str(container_id))
