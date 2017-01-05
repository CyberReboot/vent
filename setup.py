from setuptools import setup, find_packages

setup(
    name='vent',
    version='v0.3.2-dev',
    packages=['vent', 'vent.core', 'vent.core.file-drop', 'vent.core.rq-worker',
              'vent.core.rq-dashboard', 'vent.core.template-change',
              'vent.core.rmq-es-connector', 'vent.helpers'],
    data_files=[('vent/scripts', ['scripts/bootlocal.sh', 'scripts/bootsync.sh',
                                  'scripts/build.sh', 'scripts/build_images.sh',
                                  'scripts/build_local.sh', 'scripts/custom',
                                  'scripts/wrapper.sh']),
                ('vent', ['vent/help']),
    scripts=['scripts/vent-cli', 'scripts/vent', 'scripts/vent-generic'],
    license='Apache License 2.0',
    author='arpit',
    author_email='',
    maintainer='Charlie Lewis',
    maintainer_email='clewis@iqt.org',
    description='A self-contained virtual appliance based on boot2docker that provides a platform to collect and analyze data across a flexible set of tools and technologies.',
    keywords='docker containers platform collection analysis tools devops',
    url='https://github.com/CyberReboot/vent',
)
