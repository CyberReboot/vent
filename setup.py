from setuptools import setup

setup(
    name='vent',
    version='v0.4.4',
    packages=['vent', 'vent.core', 'vent.core.file_drop',
              'vent.core.rq_worker', 'vent.core.rq_dashboard', 'vent.menus',
              'vent.core.rmq_es_connector', 'vent.helpers', 'vent.api'],
    install_requires=['docker', 'npyscreen'],
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
