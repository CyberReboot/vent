.. Vent documentation master file, created by
   sphinx-quickstart on Mon Jul 17 12:58:13 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Overview
========
Vent is a library that includes a CLI designed to serve as a general platform for analyzing network traffic. Built with some basic functionality, Vent serves as a user-friendly platform to build custom ``plugins`` on to perform user-defined processing on incoming network data. Vent supports any filetype, but only processes filetypes based on the types of plugins installed for that instance of vent.

Simply create your ``plugins``, point Vent to them, install them, and drop a file in Vent to begin processing!

Dependencies
------------
::

    docker >= 1.13.1
    make (if building from source)
    pip
    python2.7.x


Getting Set Up
--------------
There's two ways to get Vent up and running on your machine:

1. Pip::

    $ pip install vent

2. Building from source (make is required)::

    $ git clone --recursive https://github.com/CyberReboot/vent.git
    $ cd vent
    $ make # (sudo may be required to install the vent command in the system bin path)

.. note:: If you already have ``docker-py`` installed on your machine, you may need to ``pip uninstall docker-py`` first. ``vent`` will install ``docker-py`` as part of the installation process. However, there are known incompatibilities of ``docker-py`` with older versions.

Once installed, it's simply::

    $ vent


Contributing to Vent
====================

Want to contribute?  Awesome!  Issue a pull request or see more `details here`_.

See `this`_ for a crash course on npyscreen: the GUI used by Vent!

.. _details here: https://github.com/CyberReboot/vent/blob/master/CONTRIBUTING.md
.. _this: https://media.readthedocs.org/pdf/npyscreen/latest/npyscreen.pdf

|

.. toctree::
  :maxdepth: 2
  :caption: Vent Basics

  quickstart

  core_and_plugins

  system_command

  build_plugin

  troubleshoot

  contributing

  new_release

.. toctree::
  :maxdepth: 1
  :caption: Vent Code

  vent.api

  vent.core

  vent.helpers

  vent.menus


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
