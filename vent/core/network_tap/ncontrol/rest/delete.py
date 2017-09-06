import ast
import docker
import web


class DeleteR:
    """
    This endpoint is for deleting a network tap filter container
    """

    @staticmethod
    def POST():
        """
        Send a POST request with a docker container ID and it will be deleted.

        Example input: {'id': "12345"}, {'id': ["123", "456"]}
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

        # delete containers chosen from CLI
        try:
            for container_id in payload['id']:
                c.containers.get(container_id).remove()
        except Exception as e:  # pragma: no cover
            return (False, 'unable to delete containers because: '
                    + str(e))

        return (True, 'container successfully deleted: ' + str(payload['id']))
