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
