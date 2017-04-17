import docker
import os
import platform

def Version():
    version = ''
    try:
        path = os.path.realpath(__file__)
        path = '/'.join(path.split('/')[:-2])
        with open(os.path.join(path, 'VERSION'), 'r') as f:
            version = f.read().split('\n')[0].strip()
    except Exception as e: # pragma: no cover
        pass
    return version

def System():
    return platform.system()

def Docker():
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
