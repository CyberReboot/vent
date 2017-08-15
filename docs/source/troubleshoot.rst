***************
Troubleshooting
***************

**Basic Troubleshooting**
=========================
Something not working as expected within Vent? Not a problem!
Let's first get some basic possible errors out of the way.

1. Is Docker installed and is the daemon running? Vent uses Docker heavily so
   it is necessary to have the Docker instanned and the daemon running.
2. Is this the latest version of Vent? Ways to get the latest Vent
   version:

   - Using pip::

        pip install vent && vent


Pip installs the latest *stable* release of Vent. If a problem still persists,
try using the latest developer build:

   - Using Docker::

        docker pull cyberreboot/vent
        docker run -it vent_image_id

   - Using Git::

        git clone https://github.com/CyberReboot/vent
        cd vent && make && vent

|

**In-Depth Troubleshooting**
============================
Still not working? That's fine! Let's get into the nitty gritty and
try to figure out what went wrong.


Is it Vent that's causing the problem?
--------------------------------------
Firstly, let's see if it's Vent that's causing the problems.
Go to the ``User Data`` folder and open up ``vent.log`` with your favorite
text editor. Let's search the key term ``False``. Iterate through the
search results and look for ``Status of some_function: False``. This
tells us that one of Vent's core functions is not performing as
expected. Next to it, there will be an error message explaining what
went wrong.

If there's a problem with Vent's implementation, please create an issue here:
https://github.com/CyberReboot/vent/issues.


Is it a custom plugin that's causing the problem?
-------------------------------------------------
If there's no obvious error messages within `vent.log`, let's check any
added plugin tools and their containers.

Run the command ``docker logs syslog_container_id``.
This will return all information about all plugin containers and any
information regarding the error should be displayed here.
