import docker
import os
import pkg_resources
import platform

def Version():
    """ Get Vent version """
    version = ''
    try:
        version = "v"+pkg_resources.require("vent")[0].version
    except Exception as e: # pragma: no cover
        pass
    return version

def System():
    """ Get system operating system """
    return platform.system()

def Docker():
    """ Get Docker setup information """
    docker_info = {'server':{}, 'env':'', 'type':'', 'os':''}

    # get docker server version
    try:
        d_client = docker.from_env()
        docker_info['server'] = d_client.version()
    except Exception as e: # pragma: no cover
        pass

    # get operating system
    system = System()
    docker_info['os'] = system

    # check if native or using docker-machine
    if 'DOCKER_MACHINE_NAME' in os.environ:
        # using docker-machine
        docker_info['env'] = os.environ['DOCKER_MACHINE_NAME']
        docker_info['type'] = 'docker-machine'
    elif 'DOCKER_HOST' in os.environ:
        # not native
        docker_info['env'] = os.environ['DOCKER_HOST']
        docker_info['type'] = 'remote'
    else:
        # using "local" server
        docker_info['type'] = 'native'
    return docker_info

def Containers(vent=True, running=True):
    """
    Get containers that are created, by default limit to vent containers that
    are running
    """
    containers = []

    try:
        d_client = docker.from_env()
        if vent:
            c = d_client.containers.list(all=running, filters={'label':'vent'})
        else:
            c = d_client.containers.list(all=running)
        for container in c:
            containers.append((container.name, container.status))
    except Exception as e: # pragma: no cover
        pass

    return containers

def Images(vent=True):
    """ Get images that are build, by default limit to vent images """
    images = []

    try:
        d_client = docker.from_env()
        if vent:
            i = d_client.images.list(filters={'label':'vent'})
        else:
            i = d_client.images.list()
        for image in i:
            images.append((image.tags, image.short_id))
    except Exception as e: # pragma: no cover
        pass

    return images

def Tools():
    """ Get tools that exist in the manifest """
    tools = []
    # !! TODO
    return tools
