New Vent Releases
#################

Get the latest clone of Vent from https://github.com/CyberReboot/vent

1. Change the version number

   - ``setup.py``
   - ``docs/source/conf.py``

2. Edit ``CHANGELOG.md`` and include a list of changes that were made. Please
   follow previous formatting.

3. Enter the ``dev`` directory and run ``Make``. This will create an ISO of
   release version of Vent. Please be patient as this step will take some time.

4. Let's ensure the ISO is correct.

   - in the directory where the ISO is located::

       python -m SimpleHTTPServer

   - We'll be using docker to create a **VirtualBox** container for this step.
     This step will also take a considerable amount of time::

       docker-machine create -d virtualbox --virtualbox-boot2docker-url http://localhost:8000/vent.iso vent

   - Let's run docker container containing the VM containing the ISO::

       docker-machine ssh vent

   An instance of Vent should appear with the new version number given above.

5. Now let's upload the release to pypi assuming there's an account with admin
   access and a corresponding ``.pypirc``::

     python setup.py sdist upload

6. Finally, change the version number to the next version number.
   Eg: ``0.4.4.dev``

