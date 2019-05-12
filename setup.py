from setuptools import setup

setup(
    name='vent',
    version='v0.9.1',
    packages=['vent', 'vent.core', 'vent.core.file_drop',
              'vent.core.rq_worker', 'vent.extras.rq_dashboard', 'vent.menus',
              'vent.extras.network_tap', 'vent.extras.network_tap.ncontrol',
              'vent.extras.rmq_es_connector', 'vent.helpers', 'vent.api'],
    install_requires=['docker>=3.7.2', 'npyscreen>=4.10.5', 'pyyaml>=5.1'],
    scripts=['bin/vent'],
    license='Apache License 2.0',
    author='arpit',
    author_email='',
    maintainer='Charlie Lewis',
    maintainer_email='clewis@iqt.org',
    description=('A library that includes a CLI designed to serve as a'
                 ' platform to collect and analyze data across a flexible set'
                 ' of tools and technologies.'),
    keywords='docker containers platform collection analysis tools devops',
    url='https://github.com/CyberReboot/vent',
)
