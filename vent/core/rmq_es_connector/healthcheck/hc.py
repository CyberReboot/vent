from flask import Flask

from healthcheck import EnvironmentDump
from healthcheck import HealthCheck

app = Flask(__name__)

health = HealthCheck(app, '/healthcheck')
envdump = EnvironmentDump(app, '/environment')


def application_data():
    return {'maintainer': 'Charlie Lewis',
            'git_repo': 'https://github.com/CyberReboot/vent',
            'app': 'rmq_es_connector'}


envdump.add_section('application', application_data)
