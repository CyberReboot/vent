def file_queue(path):
    """
    Processes files that have been added from the rq-worker, starts plugins
    that match the mime type for the new file.
    """
    import docker
    import magic
    import os
    import time

    d_client = docker.from_env()
    #d_client.containers.run()

    return
