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

        # if user gives a list of id, delete them all
        if isinstance(payload['id'], list):
            try:
                for container_id in payload['id']:
                    c.containers.get(container_id).remove()
            except Exception as e:  # pragma: no cover
                return (False, 'unable to delete list of containers because: '
                        + str(e))
        # if user gives just one id, delete it
        else:
            try:
                c.containers.get(payload['id']).remove()
            except Exception as e:  # pragma: no cover
                return (False, 'unable to delete container because: ' + str(e))

        return (True, 'container successfully deleted: ' + str(payload['id']))
