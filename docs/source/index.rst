.. Vent documentation master file, created by
   sphinx-quickstart on Mon Jul 17 12:58:13 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Vent's documentation!
================================

> Network Visibility (an anagram)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/792bc7e54645427581da66cd6847cc31)](https://www.codacy.com/app/clewis/vent?utm_source=github.com&utm_medium=referral&utm_content=CyberReboot/vent&utm_campaign=badger)
[![Build Status](https://travis-ci.org/CyberReboot/vent.svg?branch=master)](https://travis-ci.org/CyberReboot/vent)
[![Documentation Status](https://readthedocs.org/projects/vent/badge/?version=latest)](http://vent.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/vent.svg)](https://badge.fury.io/py/vent)
[![codecov](https://codecov.io/gh/CyberReboot/vent/branch/master/graph/badge.svg)](https://codecov.io/gh/CyberReboot/vent)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/ffe3b2d6a9254b98a12de6b3273676b3/badge.svg)](https://www.quantifiedcode.com/app/project/ffe3b2d6a9254b98a12de6b3273676b3)
[![Github Release Downloads](https://img.shields.io/github/downloads/cyberreboot/vent/total.svg?maxAge=2592000)](https://github.com/CyberReboot/vent/releases)
[![Docker Hub Downloads](https://img.shields.io/docker/pulls/cyberreboot/vent-elasticsearch.svg)](https://hub.docker.com/u/cyberreboot)

            '.,
              'b      *
               '$    #.
                $:   #:
                *#  @):
                :@,@):   ,.**:'
      ,         :@@*: ..**'
       '#o.    .:(@'.@*"'
          'bq,..:,@@*'   ,*
          ,p$q8,:@)'  .p*'
         '    '@@Pp@@*'
               Y7'.'
              :@):.
             .:@:'.
           .::(@:.
                       _
      __   _____ _ __ | |_
      \ \ / / _ \ '_ \| __|
       \ V /  __/ | | | |_
        \_/ \___|_| |_|\__|

overview
====
Vent is a library that includes a CLI designed to serve as a general platform for analyzing network traffic. Built with some basic functionality, Vent serves as a user-friendly platform to build custom `plugins` on to perform user-defined processing on incoming network data. Vent supports any filetype, but only processes filetypes based on the types of plugins installed for that instance of vent.

Simply create your `plugins`, point Vent to them, install them, and drop a file in vent to begin processing!

### Dependencies

```
docker>=1.13.1
make (if building from source)
pip
python2.7.x
```

### Installing

```
pip install vent
```

### Getting the bits and building

```
git clone --recursive https://github.com/CyberReboot/vent.git
cd vent
make # (sudo may be required to install the vent command in the system bin path)
```

_Note - If you already have `docker-py` installed on your machine, you may need to_ `pip uninstall docker-py` _first. `vent` will install `docker-py` as part of the installation process, however there are known incompatibilities of `docker-py` with older versions._

### running

```
vent
```

Contributing to vent
====

Want to contribute?  Awesome!  Issue a pull request or see more details [here](https://github.com/CyberReboot/vent/blob/master/CONTRIBUTING.md).

See [this](https://media.readthedocs.org/pdf/npyscreen/latest/npyscreen.pdf) for a crash course on npyscreen: the GUI used by Vent!


.. toctree::
   :maxdepth: 2
   :caption: Api Functions

   vent.api


.. toctree::
   :maxdepth: 2
   :caption: Core

   vent.core


.. toctree::
   :maxdepth: 2
   :caption: Helper Functions

   vent.helpers


.. toctree::
   :maxdepth: 2
   :caption: Menu Functions

   vent.menus

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
