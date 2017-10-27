.. _userdata-label:

User Data
#########

The User Data directory is listed on the Vent main menu. Here you can find five
files and two directories here.

Files
=====

plugin_manifest.cfg
-------------------
Meta data about all built core and plugin tools.

status.json
-----------
All data regarding finished jobs is written to this JSON file. This file actually doesn't
exist until a job is processed and **completed**. Each tool will get it's own
JSON entry. If there were two tools that ran and finished, there will be one
entry for each tool.

vent.cfg
--------
A configuration file used to customize Vent and its processes.

-main
^^^^^
  *files*
    The directory of ``File Drop``. For example, if ``files = /opt/vent_files``,
    Vent will monitor for any new files in that directory.

  *service_uri*
    Override the default POST name for all services. So, let's say Vent has
    ``Elasticsearch`` at URL ``0.0.0.0:3772``.

    By adding::

        service_uri = 5.5.5.5

    under the main section, the URL for ``Elasticsearch`` is now
    ``5.5.5.5:3772``.

-network-mapping
^^^^^^^^^^^^^^^^
  *nic_name*
    The option here can be whatever is desired. The value is the nic that the
    plugin tool ``replay_pcap`` will replay to.

    For example::

        my_nic = enp0s25

    Now the plugin tool ``replay_pcap`` will mirror whatever given pcap files to
    ``enp0s25``.

    Currently, only one nic at a time is supported.


-nvidia-docker-plugin
^^^^^^^^^^^^^^^^^^^^^
  *port*
    Override port for the Nvidia docker plugin

  *host*
    Override the host for the Nvidia docker plugin

-external-services
^^^^^^^^^^^^^^^^^^
Name of tool we want Vent to use externally rather than internally.
For example, if there is already an ``Elasticsearch`` service that a user wants
Vent to use rather than Vent's internal ``Elasticsearch``, we could write::

    [external-services]
    Elasticsearch = {"ip_address": "172.10.5.3", "port": "9200",
    "locally_active": "yes"}

If a port is not specified, then it defaults to core tool's default port.
Also, you can toggle whether you want to use the local docker container
that vent utilizes or the external service by switching locally_active
between yes and no.

-groups
^^^^^^^
  *start_order*
    The order in which the tool groups are started in csv format. For example::

        core,pcap,replay

    means that core tools are started first, then any tool in the ``pcap``
    group, and lastly any tool in the ``replay`` group. Within those groups,
    plugin priority will determine the start order of the tools.

vent.init
---------
This file only tells Vent if this is the first time Vent is running so the
tutorial can be the first menu listed rather than Vent's main menu.

vent.log
--------
Log file that keeps track of the statuses of Vent's functionality. It lists what
action is taking place and shows a list of steps taken to perform that action.
So if something goes wrong, this file is a good place to start to find out what
the problem is.


Directories
===========

.internals
----------
This is a folder that Vent clones to when dealing with core tools. So when Vent
adds or builds core tools, this is the working directory.

plugins
-------
This folder deals with any plugin tools with the same philosophy as the
``.internals`` directory.
