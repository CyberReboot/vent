New Vent Releases
#################

Get the latest clone of Vent from https://github.com/CyberReboot/vent

1. Change the version number

   - ``setup.py``
   - ``docs/source/conf.py``

2. Edit ``CHANGELOG.md`` and include a list of changes that were made. Please
   follow previous formatting.

3. Run list of authors and put in `AUTHORS` to make sure it is up to date::

     git log --format='%aN <%aE>' | sort -f | uniq

4. Commit the changes, open a PR, and merge into ``master``.

5. Enter the ``dev`` directory and run ``Make``. This will create an ISO of
   release version of Vent. Please be patient as this step will take some time.

6. Let's ensure the ISO is correct.

   - In the directory where the ISO is located::

       python -m SimpleHTTPServer

   - We'll be using docker to create a **VirtualBox** VM for this step.
     This step will also take a considerable amount of time::

       docker-machine create -d virtualbox --virtualbox-boot2docker-url http://localhost:8000/vent.iso vent

   - Let's SSH into the VM created from the ISO that is running Vent

       docker-machine ssh vent

   An instance of Vent should appear with the new version number given above.

7. Now let's upload the release to pypi assuming there's an account with admin
   access and a corresponding ``.pypirc``::

     python setup.py sdist upload

8. Create a new github release. Tag and release title are the version number.
   Since we already added changes to our ``CHANGELOG.md``, there's no need to
   rewrite all that information so leave it blank. Attach the ISO and publish the release

9. Finally, change the version number to the next version number with a ``dev``
   tag. Eg: ``0.4.4.dev``. Commit the version change, make a PR, and merge to ``master``.
