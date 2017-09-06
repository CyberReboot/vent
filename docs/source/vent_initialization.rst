Vent Initialization
###################

This page describes the different actions that vent takes upon
initialization.

File Structure
==============
Vent will set up the necessary file structure to store all of the
:ref:`userdata-label`

Auto-Install
============
Vent will detect if there are any vent images already running before an
instance of itself is instantiated, and will automatically install the
tools that correspond to that image without you having to do anything.

Startup
=======
Before initialization you can specify a certain set of tools that you want
vent to install once it starts up for the first time. You can do this by
writing a .vent-startup.yml file in your home directory. The syntax for
this yaml file is as follows::

    repo_name:
      tool_name:
        <additional settings you want>

A thing to note, tool_name here means the name of the directory in which
the Dockerfile and vent.template for the tool can be found. If you have
multiple tools defined in the same directory, then use the syntax @tool_name
to differentiate between the different tools in that directory. A lot of
the additional settings you can configure are the same as what you would do
for :ref:`customventplugin-label`. These additional settings will be used
to update the default settings for that tool (as defined in its vent.template),
they will not overwrite the default settings. Besides those settings, there are
some that are specific just to this startup file:

*build*
    If you set build to yes, then the tool will be installed and then built
    immediately rather than just installed.

*start*
    If you set start to yes, then the tool will be started immediately. **Note**,
    you have to set build to yes for a tool in order for you to be able to set
    start to yes as well.

*branch*
    For tools installed from a repo, if you want to install the tools from a
    specific branch of the repo, specify it with the branch keyword. By default,
    the master branch will be where the tools are installed from.

*version*
    For tools installed from a repo, if you want to install the tools from a specific
    commit version, specify it with the version keyword. By default, the version HEAD
    will be used to install tools.

Example Startup
---------------
With that said, here is an example .vent-startup.yml file that vent could use::

    https://github.com/cyberreboot/vent:
      rabbitmq:
        build: yes 
        start: yes 
      elasticsearch:
      rq_worker:
        build: yes 
        start: yes 
        settings:
          instances: 2

This would install the tools rabbitmq, elasticsearch, and rq_worker.
Additionally, this would build and start rabbitmq and rq_worker, and
it would set the number of instances in settings to 2 for rq_worker.
