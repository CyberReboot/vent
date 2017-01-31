import os

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
