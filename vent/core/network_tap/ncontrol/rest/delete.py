import ast
import docker
import web

from nlist import ListR


class DeleteR:
    """
    This endpoint is for deleting a network tap filter container
    """

    @staticmethod
    def POST():
        """
        Send a POST request with a docker container ID and it will be deleted.
        Can also send 'all' as the ID and every network tap container will be
        deleted.

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

        # delete all network tap containers if keyword 'all' is given
        if payload['id'] == 'all':
            try:
                network_containers = ListR.GET()
                for container in network_containers:
                    c.containers.remove(container['id'])
            except Exception as e: # pragma no cover
                return 'unable to delete multiple containers because' + \
                       str(e)

        # if user gives a list of id, delete them all
        elif type(payload['id']) == list:
            try:
                for container_id in payload['id']:
                    c.containers.remove(container_id)
            except Exception as e: # pragma: no cover
                return 'unable to delete list of containers because: ' + str(e)
        # if user gives just one id, delete it
        else:
            try:
                c.containers.remove(payload['Id'])
            except Exception as e: # pragma: no cover
                return 'unable to delete container because: ' + str(e)

        return ('container successfully deleted: ' + str(payload['id']))
