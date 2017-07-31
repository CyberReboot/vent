import docker
import web

from nlist import ListR


class StartR:
    """
    This endpoint is for starting a network tap container
    """

    @staticmethod
    def POST():
        """
        Send a POST request with a docker container ID and it will be started.
        Can also send 'all' as the ID and every network tap container will be
        started.

        Example input: {'id': "12345"} or {'id': "all"}
        """
        web.header('Content-Type', 'application/json')

        # verify that user gave an ID
        data = web.data()
        payload = {}
        try:
            payload = ast.literal_eval(data)
        except Exception as e: # pragma: no cover
            return 'malformed payload : ' + str(e)

        # verify payload has a container ID
        if 'id' not in payload:
            return 'payload missing container id'

        # connect to docker and stop the given container
        c = None
        try:
            c = docker.from_env()
        except Exception as e: # pragma: no cover
            return 'unable to connect to docker because: ' + str(e)

        # start all network tap containers if keyword 'all' is given
        if payload['id'] == 'all':
            try:
                network_containers = ListR.GET()
                for container in network_containers:
                    c.containers.start(container['id'])
            except Exception as e: # pragma no cover
                return 'unable to start multiple docker containers because' + \
                       str(e)
        else:
            try:
                c.containers.start(payload['Id'])
            except Exception as e: # pragma: no cover
                return 'unable to start docker container because: ' + str(e)

        return ('container successfully started: ' + str(payload['id']))
