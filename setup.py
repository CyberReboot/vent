from setuptools import setup, find_packages

setup(
    name='vent',
    version='v0.3.2-dev',
    packages=['vent', 'vent.core', 'vent.core.file-drop',
              'vent.core.rq-worker', 'vent.core.rq-dashboard',
              'vent.core.rmq-es-connector', 'vent.helpers', 'vent.api'],
    data_files=[('vent', ['vent/help'])],
    install_requires=['docker', 'npyscreen'],
    scripts=['bin/vent-cli', 'bin/vent', 'bin/vent-generic'],
    license='Apache License 2.0',
    author='arpit',
    author_email='',
    maintainer='Charlie Lewis',
    maintainer_email='clewis@iqt.org',
    description='A library that includes a CLI designed to serve as a platform to collect and analyze data across a flexible set of tools and technologies.',
    keywords='docker containers platform collection analysis tools devops',
    url='https://github.com/CyberReboot/vent',
)
