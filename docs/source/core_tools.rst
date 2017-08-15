Core Tools
##########

**Core Tool Explanations**
**************************
There are currently nine core tools that Vent uses.

elasticsearch
=============

file_drop
=========
Description goes here

network_tap
===========
A container that will watch a specific nic using **tcpdump** to output pcap
files based on what was monitored. Has an interface located in ``System
Commands -> Network Tap Interface``. The interface has five available actions:

- **Create**: Create a new container with a specified nic, tag, interval (in *seconds*),
  filter, and iterations. The container is also automatically started.
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
Description goes here

rmq_es_connector
================
A gateway between rabbitmq and elasticsearch. This way, a user is not locked
into using rabbitmq.

rq_worker
=========
Description goes here

rq_dashboard
============
Description goes here

syslog
======
Standard logging system that adheres to the syslog standard. Modular. Can be
replaced with user provided syslog system.

|

**Core Tool Actions**
*********************

Short explanations of all actions available in the core tools sub-menu.

Add all latest core tools
=========================
Clone the latest core tools from `cyberreboot/vent`_. This will **not** update or
remove any core tool images that have already been added. All added tools are also
added to ``plugin_manifest.cfg`` located in the ``User Data`` folder.

.. _cyberreboot/vent: https://github.com/CyberReboot/vent/

Build core tools
================
Build docker images from the Dockerfiles obtained above.
This is essentially running ``docker build .`` in each core tool's respective
directory.

Clean core tools
================

Configure core tools
====================
Edit a core tool's vent.template folder found in the tool's respective folder
located in ``vent/core/``. Read more about vent template folders `here`_.

.. _here: https://google.com

Disable core tools
==================

Enable core tools
=================

Inventory of core tools
=======================
Provides meta data regarding currently added core tools. It tells if a core tool is built,
enabled, the name of the image, and the if the tool is currently running.

Remove core tools
=================
Remove the tool's image from ``plugin_manifest.cfg``. The tool must be added again if it is
to be built.

Start core tools
================
Start the tools' respective containers. Similar to executing the command
``docker run -it tool_id``.

Stop core tools
===============
Stop the tools' respective containers. Similar to executing the command
``docker stop tool_id``.

Update core tools
=================
