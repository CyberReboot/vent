import ast
import docker
import web


class StopR:
    """
    This endpoint is for stopping a network tap filter container
    """

    @staticmethod
    def POST():
        """
        Send a POST request with a docker container ID and it will be stopped.

        Example input: {'id': "12345"}, {'id': ["123", "456"]
        """
        web.header('Content-Type', 'application/json')

        # verify user input
        data = web.data()
        payload = {}
        try:
            payload = ast.literal_eval(data)
        except Exception as e:  # pragma: no cover
            return (False, 'malformed payload : ' + str(e))

        # verify payload has a container ID
        if 'id' not in payload:
            return (False, 'payload missing container id')

        # connect to docker and stop the given container
        c = None
        try:
            c = docker.from_env()
        except Exception as e:  # pragma: no cover
            return (False, 'unable to connect to docker because: ' + str(e))

        # stop containers chosen from CLI
        try:
            for container_id in payload['id']:
                c.containers.get(container_id).stop()
        except Exception as e:  # pragma: no cover
            return (False, 'unable to stop list of containers because: ' +
                    str(e))

        return (True, 'container successfully stopped: ' + str(payload['id']))
