import ast
import docker
import web

from nlist import ListR


class StartR:
    """
    This endpoint is for starting a network tap filter container
    """

    @staticmethod
    def POST():
        """
        Send a POST request with a docker container ID and it will be started.
        Can also send 'all' as the ID and every network tap container will be
        started.

        Example input: {'id': "12345"}, {'id': ["123", "456"]}, or {'id': "all"}
        """
        web.header('Content-Type', 'application/json')

        # verify user input
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
        # TODO: figure out how to implement all without reinventing the wheel
        # if payload['id'] == 'all':
        #    try:
        #        network_containers = ListR.GET()
        #        for container in network_containers:
        #            c.containers.get(container['id']).start()
        #    except Exception as e: # pragma no cover
        #        return 'unable to start multiple containers because' + \
        #               str(e)

        # if user gives a list of id, start them all
        if type(payload['id']) == list:
            try:
                for container_id in payload['id']:
                    c.containers.get(container_id).start()
            except Exception as e: # pragma: no cover
                return 'unable to start list of containers because: ' + str(e)

        # if user gives just one id, start it
        else:
            try:
                c.containers.get(payload['id']).start()
            except Exception as e: # pragma: no cover
                return 'unable to start container because: ' + str(e)

        return ('container successfully started: ' + str(payload['id']))
