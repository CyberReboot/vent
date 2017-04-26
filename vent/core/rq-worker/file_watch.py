def file_queue(path):
    """
    Processes files that have been added from the rq-worker, starts plugins
    that match the mime type for the new file.
    """
    import ConfigParser
    import docker
    import magic
    import os
    import time

    d_client = docker.from_env()

    # TODO read in configuration of plugins to get the ones that should run against the path.

    # TODO add connections to syslog, and file path etc.

    # TODO start containers

    #d_client.containers.run()

    return
