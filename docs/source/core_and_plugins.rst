Core Tools and Plugins
######################

Core Tool Explanations
**************************
There are currently nine core tools that Vent uses.

elasticsearch
=============
Indexes text for full text search. Enables comprehensive text search of syslog.

file_drop
=========
Watches the specified directory for any new files. If a new file is added, it is
added to a ``redis`` queue.

network_tap
===========
A container that will watch a specific nic using **tcpdump** to output pcap
files based on what was monitored. Has an interface located in ``System
Commands -> Network Tap Interface``. The interface has five available actions:

- **Create**: Create a new container with a specified nic, tag, interval (in *seconds*),
  filter, and iterations. The container is also automatically started on
  creation.
- **Start**: Start a network tap container. Uses the settings specified in ``create``
  to run.
- **Stop**: Stop a network tap container.
- **List**: Show all network tap containers. Will return container's ID, if the container is
  running or not, and the tag provided in ``create``.
- **Delete**: Delete a specified network tap container. Containers *must be stopped* before they
  are able to be deleted.

rabbitmq
========
Formats messages received from syslog and sends the formatted messages to
rmq_es_connector.

redis
=====
The queuing system that ``file drop`` sends to and ``rq_worker`` pulls out of.

rmq_es_connector
================
A gateway between ``rabbitmq`` and ``elasticsearch``. This way, the message
formatting system does not have to be ``rabbitmq``.

rq_worker
=========
The tool that takes files from the ``redis`` queue and runs the plugins that deal with
those file extensions.

rq_dashboard
============
Management console to look at rq_worker's active queue.

syslog
======
Standard logging system that adheres to the syslog standard. All containers send
their information to syslog.

|

Core Tool and Plugin Actions
****************************

Short explanations of all actions available in the core tools and plugins sub-menu.

Add all latest core/plugin tools
================================
Clone the latest version of the tool. This will **not** update or
remove any tools that have already been added.

By default, core tools are cloned from `cyberreboot/vent`_ and plugins, if no
custom repo is specified, are cloned from `cyberreboot/vent-plugins`_.

.. _cyberreboot/vent: https://github.com/CyberReboot/vent/
.. _cyberreboot/vent-plugins: https://github.com/CyberReboot/vent-plugins/

Build core/plugin tools
=======================
Build docker images from the Dockerfiles obtained from adding.

Clean core/plugin tools
=======================
Stop and remove the chosen tools' containers.

Configure core/plugin tools
===========================
Edit a tool's vent.template file found in the tool's respective folder.
Read more about :ref:`venttemplate-label`

Disable core/plugin tools
=========================
Remove chosen tools from menus. For example, let's say there were ten tools but only
five were needed. Disabling the five unneeded tools would stop the tools from
appearing on the menus.

Enable core/plugin tools
========================
Opposite of disable tools. Enables the tools so they can be seen again.

Inventory of core/plugin tools
==============================
Provides meta data regarding currently added core/plugin tools. It tells if a tool is built,
enabled, the name of the image, and the if the tool is currently running.

Remove core/plugin tools
========================
Remove a tool entirely. Any of that tool's containers are also stopped and
deleted. The tool must be added again if it is to be used.

Start core/plugin tools
=======================
Start the tools' respective containers. Similar to executing the command
``docker run -it tool_id``.

Stop core/plugin tools
======================
Stop the tools' respective containers. Similar to executing the command
``docker stop tool_id``.

Update core/plugin tools
========================
Pulls the latest commit of the tool and builds it.
