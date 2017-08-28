import docker
import web


class NICsR:
    """
    This endpoint is for listing all available network interfaces
    """

    @staticmethod
    def GET():
        web.header('Content-Type', 'text/html')

        # connect to docker
        try:
            d_client = docker.from_env()
        except Exception as e:  # pragma: no cover
            return (False, 'unable to connect to docker because: ' + str(e))

        # start container to get network interfaces
        nics = ""
        try:
            nics = d_client.containers.run('cyberreboot/gonet',
                                           network_mode='host')
        except Exception as e:  # pragma: no cover
            return (False, "Failure: " + str(e))

        return (True, nics)
