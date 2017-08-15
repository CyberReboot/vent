Custom Vent Plugins
############################

Building custom vent plugins is an easy process.

Each custom vent plugin needs at least a ``Dockerfile`` and a ``vent.template``.
Read more about ``Dockerfile`` `here`_.

.. _here: https://docs.docker.com/engine/reference/builder/


.. _venttemplate-label:

Vent.template Files
===================
Vent template files are what Vent uses to build images it recognizes. They're
written and processed like ``.cfg`` files.

docker
------
Parameters for a python ``docker run`` command.
Read the `Docker python api parameters`_ for possible options.

.. _Docker python api parameters: https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run


gpu
---
Vent plugins can run on solely on GPU if specified. This section sets the
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


info
----
All metadata about the custom plugin goes under this section.

*groups*
  the group a plugin belongs to.

*name*
  the plugin's name.


service
-------
*uri_prefix*
  text goes here


settings
--------
?

*ext_types*
  Whatever this option is set to is the file extension that Vent will run this plugin on.
  For example, ``ext_types = jpg`` means Vent will run this plugin if a ``.jpg``
  file is placed in ``File Drop``.

*mime_types*
  text goes here

*priority*
  text goes here

*process_base*
  text goes here

*process_from_tool*
  text goes here

|

Example Custom Vent Plugin
==========================
Let's create a Vent plugin that uses ``cat`` to output the contents of a
``.example`` file. Let's create a ``vent_plugin_example`` and enter it.

First, let's create a simple ``bash`` script that will ``cat`` the contents of a
file.

.. code-block:: bash
   :caption: cat.sh

   #! bin/bash
   cat $1


Next, a ``Dockerfile`` is needed so let's make it.

.. code-block:: bash
   :caption: Dockerfile

   FROM ubuntu:latest
   ADD cat.sh .
   ENTRYPOINT ["/cat.sh"]
   CMD [""]


Lastly, a ``vent.template`` file is needed so Vent knows how to use the plugin.

.. code-block:: bash
   :caption: vent.template

   [info]
   name = example plugin
   groups = example

   [settings]
   ext_types = example
   process_base = yes


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
seconds, the job counter on the main menu of Vent will show that 1 job is
running, and it'll finish soon after and show 1 completed job.

To check that the plugin worked and outputted ``qwerty``, let's check the syslog
container using the command ``docker logs vent_syslog_id > log_file``. Now
search log_file for ``qwerty``. It should look something like this:

::

    date/time example[some_num]: qwerty

If you see this line, congrats! You have successfully built your first Vent
plugin.

If the plugin did not function correctly, try rereading the tutorial or check
the :ref:`troubleshooting-label` guide.

Other examples can be found at `CyberReboot/vent-plugins`_.

.. _CyberReboot/vent-plugins: https://github.com/CyberReboot/vent-plugins
