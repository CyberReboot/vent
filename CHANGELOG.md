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
