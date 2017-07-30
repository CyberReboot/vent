import docker
import web


class ListR:
    """
    This endpoint is for listing a filter
    """

    @staticmethod
    def GET():
        web.header('Content-Type', 'text/html')

        # connect to docker
        try:
            containers = docker.from_env()
        except Exception as e: # pragma: no cover
            return 'unable to connect to docker because: ' + str(e)

        # search for all docker containers and grab ncapture containers
        container_list = []
        for c in containers:
            # TODO: maybe find a way to not have to hard code image name
            if c.attrs["Config"]["Image"] == \
                    "cyberreboot/vent-ncapture:master":
                # the core container is not what we want
                if "core" not in c.attrs["Config"]["Labels"]["vent.groups"]:
                    lst = c.attrs["Id"]
                    lst.append(c.attrs["Created"])
                    lst.append(c.attrs["Args"][0])
                    container_list.append(lst)
        return container_list
