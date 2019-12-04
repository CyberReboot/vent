# v0.10.1 (2019-12-04)

improvements:
- upgraded version of pytest
- upgraded version of pyyaml
- upgraded version of sphinx
- upgraded version of elasticsearch
- upgraded version of gunicorn
- removed tcpdump fork
- added RabbitMQ message upon completion of ncapture
- added option to use ncapture with a file

# v0.10.0 (2019-11-21)

improvements:
- upgraded version of urllib3
- upgraded version of elasticsearch
- upgraded version of pytest
- removed unused code
- move from tcpdump to tracepcapd for packet capture

# v0.9.15 (2019-11-07)

improvements:
- upgraded version of pytest
- upgraded version of sphinx
- upgraded version of elasticsearch
- upgraded version of six
- removed unused components: vizercal and workflow
- better logging of git errors

bug fixes:
- using pollingobserver to save kernel resources that inotify was leaking

# v0.9.14 (2019-10-24)

improvements:
- upgraded version of elasticsearch
- upgraded version of webpack
- upgraded version of webpack-dev-server
- upgraded version of monorepo
- upgraded version of redis
- upgraded version of react
- ugpraded version of react-dom

# v0.9.13 (2019-10-10)

improvements:
- upgraded version of docker
- upgraded version of monorepo
- upgraded version of url-loader
- upgraded version of eslint-plugin-react
- upgraded version of pytest-cov
- upgraded version of pytest

# v0.9.12 (2019-10-02)

improvements:
- upgraded version of elasticsearch
- upgraded version of pytest
- upgraded version of urllib3
- upgraded version of react
- upgraded version of react-dom
- upgraded version of socket.io-client
- upgraded version of eslint
- upgraded version of eslint-loader
- upgraded version of eslint-plugin-react
- upgraded version of webpack
- upgraded version of webpack-dev-server

# v0.9.11 (2019-09-17)

improvements:
- upgraded version of webpack-dev-server
- upgraded version of eslint
- upgraded version of webpack
- upgraded version of elasticsearch
- send rabbit messages from file_drop for all trace files regardless of size for Poseidon

# v0.9.10 (2019-09-12)

improvements:
- upgraded version of pytest
- upgraded version of query-string
- upgraded version of source-sans-pro
- upgraded version of eslint

# v0.9.9 (2019-08-30)

improvements:
- upgraded version of elasticsearch
- upgraded version of babel-eslint
- upgraded version of eslint
- upgraded version of eslist-loader
- upgraded version of webpack

# v0.9.8 (2019-08-20)

improvements:
- upgraded version of redis
- upgraded version of pytest
- upgraded version of eslint
- upgraded version of sphinx
- upgraded version of rq-dashboard

bug fixes:
- fixed issue where incorrect file path parsing was causing file drop to crash
- fixed issue where older version of rq-dashboard wasn't working with the newer version of RQ

# v0.9.7 (2019-08-15)

improvements:
- upgraded version of redis
- upgraded version of react
- upgraded version of react-dom
- upgraded version of css-loader
- upgraded version of eslint-config-airbnb-base
- upgraded version of file-loader
- upgraded version of rimraf
- upgraded version of style-loader
- upgraded version of webpack
- upgraded version of webpack-dev-server

# v0.9.6 (2019-08-01)

improvements:
- upgraded version of pika
- upgraded version of webpack
- upgraded version of css-loader
- upgraded version of file-loader
- upgraded version of url-loader
- upgraded version of lodash
- upgraded version of eslint-plugin-import
- upgraded version of vizceral-react
- upgraded version of rq
- upgraded version of eslint
- upgraded version of eslint-plugin-react
- upgraded version of query-string
- upgraded version of redis
- upgraded version of elasticsearch
- upgraded version of pyyaml

# v0.9.5 (2019-07-11)

improvements:
- upgraded version of pytest
- upgraded version of webpack
- upgraded version of eslint-config-airbnb-base
- upgraded version of eslint-loader
- upgraded version of flask
- upgraded version of lodash

# v0.9.4 (2019-06-27)

improvements:
- upgraded version of superagent
- upgraded verison of babel-eslint
- upgraded version of webpack-dev-server
- upgraded version of ubuntu for Docker image
- upgraded version of elasticsearch
- upgraded version of sphinx
- upgraded version of alpine for Docker image
- upgraded version of docker
- upgraded version of webpack
- upgraded version of query-string
- upgraded version of eslint
- upgraded version of eslint-plugin-react
- upgraded version of eslint-plugin-import
- upgraded version of url-loader

# v0.9.3 (2019-06-13)

improvements:
- upgraded version of pyyaml
- upgraded version of sphinx
- upgraded version of pytest
- upgraded version of webpack-dev-server
- upgraded version of vizcerral-react
- upgraded version of webpack
- upgraded version of file-loader
- upgraded version of url-loader
- upgraded version of query-string
- upgraded version of css-loader
- upgraded version of superagent

# v0.9.2 (2019-05-30)

improvements:
- upgraded version of urllib3
- upgraded version of flask
- upgraded version of docker
- upgraded node dependencies
- upgraded version of elasticsearch

# v0.9.1 (2019-05-12)

improvements:
- upgraded version of pytest-cov
- upgraded version of pytest
- upgraded version of elasticsearch
- keep track of how many plugin plugins of each type are started

# v0.9.0 (2019-05-02)

improvements:
- moved containers to their own network bridge
- upgraded version of falcon

# v0.8.3 (2019-04-18)

improvements:
- upgraded version of rq
- upgraded version of sphinx
- upgraded version of elasticsearch
- upgraded version of pika
- upgraded version of pytest

# v0.8.2 (2019-04-04)

improvements:
- upgraded version of docker
- upgraded version of pika
- upgraded version of pytest
- upgraded version of sphinx
- upgraded version of watchdog

bug fixes:
- fixed an issue where overriding the docker command for rq_worker was failing

# v0.8.1 (2019-03-21)

improvements:
- upgraded version of pyyaml
- upgraded version of docker
- upgraded version of pytest
- upgraded version of redis

# v0.8.0 (2019-03-07)

improvements:
- major rewrite reducing number of lines of code
- removed Docker binary from images
- moved non-critical tools to extras directory
- without a startup file, vent will not auto install/build/start core tools

bug fixes:
- removed shell outs to Docker
- fixed checkout of different branches where locations have changed
- fixed same name tools in different directories
- instances in template files now take effect
- fixed issue where template and startup files might disagree on number of instances

# v0.7.5 (2019-02-22)

improvements:
- upgraded to alpine 3.9
- upgraded elasticsearch to 6.6.0
- upgraded version of pytest
- upgraded version of redis

# v0.7.4 (2019-02-08)

improvements:
- upgraded version of redis
- upgraded to latest version of pip
- upgraded version of pytest
- upgraded version of sphinx

bug fixes:
- docker was accidentally removed, it has been readded correctly

# v0.7.3 (2019-01-25)

improvements:
- upgraded version of pytest
- updated version of pre-commit modules
- upgraded version of pika
- updated test build to use xenial
- cleaned up apk usage

bug fixes:
- fixed pre-commit stuff
- pinned pip to a version

# v0.7.2 (2019-01-11)

improvements:
- upgraded version of gevent
- upgraded version of pytest
- upgraded version of pytest-cov
- upgraded version of docker
- added file limits to fix too many open files issues

bug fixes:
- fixed responses from network_tap

# v0.7.1 (2018-12-28)

improvements:
- added more readme details about plugins
- handles case where volumes is a list instead of a dict
- broke up log files in unique names and directories
- no longer needs to store updates in redis for network_tap
- reduced image sizes
- broke out ip address into ipv4 and ipv6
- upgraded version of sphinx

# v0.7.0 (2018-12-14)

improvements:
- upgraded version of pytest
- upgraded version of sphinx
- upgraded version of redis
- upgraded version of elastic
- upgraded version of docker
- upgraded version of six
- upgraded version of rq
- bind core tool ports to localhost interface or not at all where applicable

bug fixes:
- multiple linked containers
- fix multiple instances of the same tool

# v0.6.9 (2018-10-22)

improvements:
- removes exited plugin containers
- remove deprecated warn logger statements
- upgraded version of sphinx
- upgraded version of pytest
- upgraded version of docker
- upgraded version of gevent
- upgraded version of gunicorn

bug fixes:
- updated gitignore to remove stale eggs

# v0.6.8 (2018-09-21)

improvements:
- upgraded version of sphinx
- persist Redis data

bug fixes:
- add back ip_addresses set

# v0.6.7 (2018-09-07)

improvements:
- upgraded version of pytest
- upgraded version of pytest-cov
- upgraded version of sphinx
- upgraded version of watchdog
- file_drop now checks for empty files and handles notifications for that
- now uses the mac address as the key rather than the IP address for network_tap

bug fixes:
- remove previously created containers with the same name before starting new ones

# v0.6.6 (2018-08-24)

improvements:
- upgraded version of gevent
- upgraded version of pytest
- upgraded version of sphinx
- ncapture now uses a fork of tcpdump with the --no-payload flag instead of -s0

bug fixes:
- adds volume for syslog log file
- typo fixed that now properly ignores misc pcaps
- fixes filter for L2 capture

# v0.6.5 (2018-08-10)

improvements:
- upgraded version of pytest
- improved syslog format to not be unnecessarily verbose
- updated to alpine 3.8
- linting
- fixed syslog warnings
- upgraded version of elasticsearch

# v0.6.4 (2018-07-27)

improvements:
- upgraded version of rq
- upgraded version of gevent
- upgraded version of sphinx
- improved tests

# v0.6.3 (2018-07-13)

improvements:
- better logging
- upgraded version of pytest
- locked python at 3.6 for gevent
- upgraded verison of pyyaml
- allow for cased paths with repos for tools
- cleaned up old scripts and flakey tests

bug fixes:
- fix issue where plugins would only update on master branch

# v0.6.2 (2018-06-29)

improvements:
- upgraded version of docker
- increase the number of client connections to syslog
- add option to exclude labels from containers running by vent
- upgraded verison of pika
- upgraded version of pytest
- upgraded version of gevent
- upgraded version of elasticsearch
- only pulls repo latest changes is specifically updating
- add healthchecks to all images
- add visibility containers (vizceral and workflow) still WIP
- updated elasticsearch image to 6, removed head plugin, works best if you also have kibana now
- only rebuild images if they can't be pulled or there are changes for them in .plugin_config.yml
- be able to specify vent.cfg options in .vent_startup.yml files

bug fixes:
- no longer forces repos to be checked out to a specific commit

# v0.6.1 (2018-06-15)

improvements:
- tests now run in parallel on travis
- upgraded version of pytest
- upgraded version of gevent
- outputs the name and ID of the container in syslog now

bug fixes:
- fixed paths in rq_worker for both vent inside and outside of a container
- fixed process_from_tool recursion issue

# v0.6.0 (2018-06-01)

improvements:
- upgraded all python2 to python3
- removed b2d ISO as it's been moved to maintenance mode
- moved from web.py to falcon for network_tap
- upgraded syslog version
- upgraded version of pytest
- pin all versions of pip dependencies
- upgraded version of rq
- increased the number of concurrent connections to syslog

bug fixes:
- fixed issue where multiple instances of a plugin wouldn't get started

# v0.5.2 (2018-05-18)

improvements:
- updated syslog-ng, also now uses Debian, which is more stable

bug fixes:
- fixed issue with file_drop path during high volume
- fixed issue where ncapture wouldn't write out timestamps

# v0.5.1 (2018-05-04)

improvements:
- added started-by and built-by labels for containers and images
- added a new endpoint to network_tap to update the metadata
- updataed version of pytest

bug fixes:
- fixed local tests

# v0.5.0 (2018-03-23)

improvements:
- rabbit now uses alpine for the image
- tcpdump terminates in the time interval correctly now
- updates dependency versions

bug fixes:
- fixes an issue where git wouldn't get right the branches
- fix for tools that are at the root of the repo
- ncontrol keeps track of the requests being made in redis
- improved logging
- fixes a mistake in the docs
- fixes naming conventions for multiple Dockerfiles at the root of a repo

# v0.4.9 (2018-03-09)

improvements:
- explictily use the default rabbitmq port instead of a random one
- update pytest version to 3.4.2
- remove need for an extra rabbitmq server in the tests
- update version of web.py to 0.39

bug fixes:
- fix root path of filedrop for running vent in a container

# v0.4.8 (2018-02-09)

improvements:
- pinned versions for dependencies and updated them to the latest

bug fixes:
- rolled back boot2docker version to pre-debian until that can be better tested
- removed quay test as it was brittle

# v0.4.7 (2017-12-15)

improvements:
- more logging
- logs the location the error occurred
- updates b2d version
- updates alpine version
- allows option to not build existing images again
- allows URI info to have more than one exposed service per tool

bug fixes:
- fixes timestamp error for rq_worker
- fixes paths for rq_worker
- fixes GPU paths for rq_worker

# v0.4.6 (2017-11-09)

improvements:
- cleaned up logging
- cleaned up docs
- removed deprecated MAINTAINER instruction in dockerfiles
- add more test coverage
- allow for configuration files for plugins and overrides for environment variables
- added an extra metadata field for network_tap

bug fixes:
- fixed issue where entries are duplicated in the editor
- moved path from /tmp to /opt so that filedrop detects files, especially on osx

# v0.4.5 (2017-09-22)

improvements:
- Vent can automatically start up tools and plugins through a
  `vent_startup.yml`. Read more about it [here]
  (http://vent.readthedocs.io/en/latest/initialization.html)
- multiple instances of `rq_worker` can exist and have its own specific options
- `network-tap` actions will prompt the user to install, start, and run the tool
  if it isn't already

bug fixes:
- actions regarding multiple checked items in any of the `network-tap` options
  now work correctly
- the job counter on the main Vent menu is now correctly counting the number of
  finished jobs
- factory reset of Vent can now deal with image dependencies and will delete
  them correctly
- the `gonet` image is now removed with a factory reset of Vent
- all `ncapture` containers are removed if `network-tap` is removed


# v0.4.4 (2017-08-25)

bug fixes:
- removed private credentials from getting logged into error messages
- added ability to add options to existing sections in vent.cfg
- fixed issue #792, wherein existing containers could not be deleted when rebuilding plugins:
- fixed issue #805, wherein vent.cfg were not mounted in rq_worker

improvements:
- added tutorials and troubleshooting forms, and updated documentation
- prevents installation of tools that have already been installed
- tests can be run locally from a docker container
- adds vent initialization status update when first vent is started
- updates the manifest for existing images and containers in use when vent first starts
- removes suplemon dependency


# v0.4.3 (2017-08-11)

improvements:
- give ability for users to configure vent.cfg with various customizations:
    - can set an option to use already running external services over locally provided containers (changes will be executed automatically after editing)
    - can set a network-mapping option that can tell tools to use specific nics
    - can set a start order for groups
- implemented an option set under system commands for running network tap so that users can more easily utilize it
- can toggle view by group for certain options
- added ability to start, stop, list, and delete containers running network tap
- can now build multiple tools defined in the same directory
- fixed docker error with rmq_es_connector
- can update a tool to latest version without having to stop and restart containers
- changing the vent.template of a tool now triggers it to restart with new settings

# v0.4.2 (2017-07-28)

improvements:
 - there is now a docker container that can run vent: `docker pull cyberreboot/vent`
 - new core tool network tap that listens on a host bound nic for collection
 - support for multi-state plugin pipelines
 - vent can now save and restore hosts from a backup
 - a user can now specify the location of where file drop watches
 - file drop can now handle recursive directories
 - data regarding finished jobs is now stored as status.json
 - documentation set up and hosted using Read the Docs: http://vent.readthedocs.io/en/latest/
 - various bug fixes

# v0.4.1 (2017-07-13)

improvements:
 - core containers automatically restart if they fail
 - added extra user action for destructive actions
 - correctly mapped filedrop path from vent.cfg
 - fixed incorrect image_id in the manifest
 - more information is stored in the manifest now
 - improvements to user experience and logging
 - added basic GPU support

# v0.4.0 (2017-06-08)

improvements:
 - complete rewrite to make things more flexible and efficient
 - wrote an API that the CLI menu leverages

# v0.3.1 (2016-12-29)

improvements:
 - put back version info when new shell is created
 - plugin_parser now throws errors as appropriate
 - reboot now prompts for confirmation
 - template parser helper functions now implemented
 - updated documentation

environment:
 - based on boot2docker 1.12.5
 - using docker 1.12.5
 - using python 2.7.13
 - using pip 9.0.1
 - using redis:alpine
 - using alpine:3.5
 - using elasticsearch 2.4.3

# v0.3.0 (2016-10-26)

bug fixes:
 - fixed the following issues: #41, #182, #184, #195, #207, #216, #217
 - fixed issue where containers were getting killed when going into the shell

improvements:
 - updated suplemon#c808217
 - restructured directories and files to make it cleaner and more structured
 - changed data path on vent instance from /data to /vent
 - experimental local install that isn't inside a virtual machine, not complete
 - updated documentation

environment:
 - based on boot2docker 1.12.2
 - using docker 1.12.2
 - using python 2.7.12

# v0.2.1 (2016-09-07)

bug fixes:
 - fixed issue where turning off local rabbitmq would break syslog and subsequent core containers
 - fixed issue where specifying a single Env for a plugin was breaking

environment:
 - based on boot2docker 1.12.1
 - using docker 1.12.1
 - using python 2.7.11

# v0.2.0 (2016-09-01)

bug fixes:
 - fixed the following issues: #38, #43, #56, #92, #109, #110, #121, #130, #134, #135, #151, #153, #154, #160, #165, #167

improvements:
 - plugins can write out new files that other plugins can pick up
 - added ext_type and mime_type as template options for plugins
 - better readability in the UI
 - updated Elasticsearch to 2.3.5
 - vent now allows vcontrol to use private repositories

new features:
 - added Visualization Endpoints to menu
    - supported: Kibana, Grafana

environment:
 - based on boot2docker 1.12.1
 - using docker 1.12.1
 - using python 2.7.11

# v0.1.3 (2016-08-01)

bug fixes:
 - fixed the following issues: #44, #78, #87, #88, #96, #128, #138

improvements:
 - added more test coverage
 - better readability in the UI

new features:
 - added helper scripts for vent to the path for easy execution
 - added perl for git submodules

environment:
 - based on boot2docker 1.12.0
 - using docker 1.12.0
 - using python 2.7.11

# v0.1.2

bug fixes:
 - fixed some bash issues
 - fixed a bug where external options didn't work
 - fixed the following issues: #39, #40, #45, #100, #108, #111, #112

improvements:
 - increased test coverage
 - recursively gets submodules for tests
 - refactored menu launcher
 - refactored template parser

new features:
 - added get_namespaces script to get namespace info
 - added new template option `public_nic` for specifying public interface to run core services on
 - added new template option `mime_types` for plugin namespaces to specify the mime_types they support
 - supports files other than just PCAPs

environment:
 - based on boot2docker 1.11.2
 - using docker 1.11.2
 - using python 2.7.11

# v0.1.1

bug fixes:
 - configparser sometimes wouldn't preserve case sensitivity
 - configparser sometimes wouldn't reset the context properly
 - fixed an issue where the menu might not have a valid menu object
 - fixed a number of small code fixes
 - fixed the following issues: #47, #48, #49, #54, #55, #57, #61, #62, #63, #67, #69, #77, #80, #89

improvements:
 - better output when operations in the menu are finished
 - increased test coverage by almost 40%
 - better documentation
 - changed many hard-coded paths to dynamic paths

new features:
 - added `Logs` as a menu option
 - added `Plugin Status: Errors` menu

environment:
 - based on boot2docker 1.11.2
 - using docker 1.11.2
 - using python 2.7.11

# v0.1.0

 - initial offering
 - allows for dynamically adding plugins
 - contains a core set of services for processing files
 - based on boot2docker 1.11.2
 - using docker 1.11.2
 - using python 2.7.11
