import datetime
import docker
import os
import pkg_resources
import platform
import subprocess

from vent.api.templates import Template
from vent.helpers.paths import PathDirs

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
            c = d_client.containers.list(all=not running, filters={'label':'vent'})
        else:
            c = d_client.containers.list(all=not running)
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

def Tools(**kargs):
    """ Get tools that exist in the manifest """
    path_dirs = PathDirs(**kargs)
    manifest = os.path.join(path_dirs.meta_dir, "plugin_manifest.cfg")
    template = Template(template=manifest)
    tools = template.sections()
    return tools[1]

def Services(vent=True):
    """
    Get services that have exposed ports, by default limit to vent containers
    """
    services = []
    try:
        d_client = docker.from_env()
        if vent:
            containers = d_client.containers.list(filters={'label':'vent'})
        else:
            containers = d_client.containers.list()
        for container in containers:
            if vent:
                name = container.attrs['Config']['Labels']['vent.name']
            else:
                name = container.name
            ports = container.attrs['NetworkSettings']['Ports']
            p = []
            for port in ports:
                if ports[port]:
                    p.append(ports[port][0]['HostIp']+":"+ports[port][0]['HostPort'])
            if p:
                services.append((name, p))
    except Exception as e: # pragma: no cover
        pass
    return services

def Core():
    """
    Get the normal core tools, and the currently installed/built/running ones,
    including custom core services
    """
    core = {'built':[], 'running':[], 'installed':[], 'normal':[]}
    # !! TODO
    # get tools from vent repo at master that are in the core group and put into normal
    # check the manifest for installed with group core
    # check docker images for built with group core
    # check docker containers for running with group core
    return core

def Timestamp():
    """ Get the current datetime in UTC """
    return str(datetime.datetime.now())+" UTC"

def Uptime():
    """ Get the current uptime information """
    return str(subprocess.check_output(["uptime"]))[1:]
