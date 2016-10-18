from distutils.core import setup

setup(
	name='vent',
	version='0.2.1',
	packages=['vent', 'vent.core', 'vent.core.file-drop', 'vent.core.rq-worker', 'vent.core.rq-dashboard',
			  'vent.core.template-change', 'vent.core.rmq-es-connector', 'vent.helpers', 'tests', 'scripts',
			  'scripts.info_tools', 'scripts.service_urls'],
	url='',
	license='Apache License',
	author='arpit',
	author_email='',
	description=''
)
