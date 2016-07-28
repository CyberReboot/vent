# v0.1.2 (current, released)

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
