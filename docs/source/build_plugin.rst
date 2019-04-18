.. _customventplugin-label:

Custom Vent Plugins
############################

Building custom vent plugins is an easy process.

Each custom vent plugin needs at least a ``Dockerfile`` and a ``vent.template``.
Read more about ``Dockerfile`` `here`_.

.. _here: https://docs.docker.com/engine/reference/builder/


.. _venttemplate-label:

Vent.template Files
===================
Vent template files are what Vent uses to build images into something it recognizes.
Listed here are sections and their various options.

Look below for examples of a ``vent.template`` file.

-docker
-------
All possible options (except links and network_mode) and their explanations are the same as the parameters for the python `Docker container run command`_.

.. _Docker container run command: https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run


-gpu
----
Vent plugins can run on solely on GPU if specified (extra ``on``). This section sets the
settings for GPU processing. At the moment, **only NVIDIA GPUs are supported**.

*dedicated*
  Should the plugin be the only process running on the GPU? If it should be, set the
  option to ``yes``. ``no`` by default.

*device*
  If you know the GPU device's number, you can set it here.

*enabled*
  Tell Vent to run the plugin on GPU

*mem_mb*
  The amount of RAM(in MB) a plugin requires.


-info
-----
All metadata about the custom plugin goes under this section.

*groups*
  the group a plugin belongs to.

*name*
  the plugin's name.


-service
--------
Appending info to an exposed port for a running service, multiple exposed ports
can be done for the same service (up to 9) by incrementing the value of 1 at
the end of each settings to correspond to the order of the ports exposed for
that service.

*uri_prefix1*
  Services a tool exposes that need a more specific URI at the beginning

*uri_postfix1*
  Services a tool exposes that need a more specific URI at the end

*uri_user1*
  Services a tool exposes that need a username

*uri_pw1*
  Services a tool exposes that need a password


-settings
---------
Options that specify how the plugin will run.

*ext_types*
  Whatever this option is set to is the file extension that Vent will run this plugin on.
  For example, ``ext_types = jpg`` means Vent will run this plugin if a ``.jpg``
  file is placed in ``File Drop``.

*priority*
  Set the order in which tools get started. If a tool belongs to more than one
  group, it's possible to specify priorities for each group. The priorities are
  comma separated and in the same order that the groups are specified.

*process_base*
  Files put in ``File Drop`` by a user or process outside of Vent will get
  processed. This option is set to ``yes`` by default.

*process_from_tool*
  Allows to specify if the tool should process files that are outputs from
  other tools specifically.

*instances*
  Allows you to specify how many instantiations of a tool you want running.
  For example, you could have two instances of rq_worker running. This would
  create two rq_worker containers, which would be useful for scaling larger
  amounts of work.

|

Example Custom Vent Plugin
==========================
Let's create a simple Vent plugin that uses ``cat`` to output the contents of a
``.example`` file. Let's create a ``vent_plugin_example`` directory and enter it.

First, let's create a simple ``bash`` script that will ``cat`` the contents of a
file.

.. code-block:: bash
   :caption: cat.sh

   #!bin/bash
   cat $1


Next, a ``Dockerfile`` is needed so let's make it.

.. code-block:: bash
   :caption: Dockerfile

   FROM ubuntu:latest
   ADD cat.sh .
   ENTRYPOINT ["/cat.sh"]
   CMD [""]


Lastly, a ``vent.template`` file is needed so Vent knows how to use the plugin:

.. code-block:: bash
   :caption: vent.template

   [info]
   name = example plugin
   groups = example

   [settings]
   ext_types = example

Here's an example of this plugin using GPUs to do work:

.. code-block:: bash
   :caption: vent.template

   [info]
   name = example plugin
   groups = example

   [settings]
   ext_types = example

   [gpu]
   enabled = yes
   mem_mb = 1024
   dedicated = yes


We need to add this to either a git repo or the docker hub. Let's use git.
Push the ``vent_plugin_example`` into some repo.

Let's now add the custom plugin to Vent. From the plugins sub-menu, select
``Add new plugin`` and enter the fields with whatever repo
``vent_plugin_example`` was pushed to. After, select the branch, commit and leave
``build`` to ``True``. Now select ``example_plugin`` and hit ``OK``. Vent will
now build the custom plugin.

To test, let's create a test file.

.. code-block:: bash
   :caption: test.example

   qwerty


Finally, with Vent and the plugin up and running and all core tools added, built,
and running, let's drop ``test.example`` into ``File Drop``. After a few
seconds, the job counter on the main menu of Vent will show that one job is
running, and it'll finish soon after and show one completed job.

To check that the plugin worked and outputted ``qwerty``, let's check the syslog
container using the command ``docker logs cyberreboot-vent-syslog-master | grep
qwerty``.

If you see this line, congrats! You have successfully built your first Vent
plugin.

If the plugin did not function correctly, try rereading the tutorial or check
the :ref:`troubleshooting-label` guide.

Other examples of custom plugins can be found at `CyberReboot/vent-plugins`_.

.. _CyberReboot/vent-plugins: https://github.com/CyberReboot/vent-plugins
