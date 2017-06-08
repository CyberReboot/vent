vent
====

> Network Visibility (an anagram)

[![Build Status](https://travis-ci.org/CyberReboot/vent.svg?branch=master)](https://travis-ci.org/CyberReboot/vent)
[![Documentation Status](https://readthedocs.org/projects/vent/badge/?version=latest)](http://vent.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/vent.svg)](https://badge.fury.io/py/vent)
[![codecov](https://codecov.io/gh/CyberReboot/vent/branch/master/graph/badge.svg)](https://codecov.io/gh/CyberReboot/vent)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/ffe3b2d6a9254b98a12de6b3273676b3/badge.svg)](https://www.quantifiedcode.com/app/project/ffe3b2d6a9254b98a12de6b3273676b3)
[![Github Release Downloads](https://img.shields.io/github/downloads/cyberreboot/vent/total.svg?maxAge=2592000)](https://github.com/CyberReboot/vent/releases)

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
vent is a library that includes a CLI designed to serve as a general platform for analyzing network traffic. built with some basic functionality, vent serves as a user-friendly platform to build custom `plugins` on to perform user-defined processing on incoming network data. vent supports any filetype, but only processes ones based on the types of plugins installed for that instance of vent.

simply create your `plugins`, point vent to them & install them, and drop a file in vent to begin processing!

### dependencies

```
docker>=1.13.1
make (if building from source)
pip
python2.7.x
```

### installing

```
pip install vent
```

### getting the bits and building

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

contributing to vent
====

Want to contribute?  Awesome!  Issue a pull request or see more details [here](https://github.com/CyberReboot/vent/blob/master/CONTRIBUTING.md).

See [this](https://media.readthedocs.org/pdf/npyscreen/latest/npyscreen.pdf) for a crash course on npyscreen: the GUI used by Vent!
