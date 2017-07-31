import ast
import docker
import web


class StartR:
    """
    This endpoint is for starting a network tap filter container
    """

    @staticmethod
    def POST():
        """
        Send a POST request with a docker container ID and it will be started.

        Example input: {'id': "12345"}, {'id': ["123", "456"]}
        """
        web.header('Content-Type', 'application/json')

        # verify user input
        data = web.data()
        payload = {}
        try:
            payload = ast.literal_eval(data)
        except Exception as e:  # pragma: no cover
            return 'malformed payload : ' + str(e)

        # verify payload has a container ID
        if 'id' not in payload:
            return 'payload missing container id'

        # connect to docker and stop the given container
        c = None
        try:
            c = docker.from_env()
        except Exception as e:  # pragma: no cover
            return 'unable to connect to docker because: ' + str(e)

        # if user gives a list of id, start them all
        if isinstance(payload['id']) == list:
            try:
                for container_id in payload['id']:
                    c.containers.get(container_id).start()
            except Exception as e:  # pragma: no cover
                return 'unable to start list of containers because: ' + str(e)

        # if user gives just one id, start it
        else:
            try:
                c.containers.get(payload['id']).start()
            except Exception as e:  # pragma: no cover
                return 'unable to start container because: ' + str(e)

        return ('container successfully started: ' + str(payload['id']))
