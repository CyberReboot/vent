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

5. Now let's upload the release to pypi assuming there's an account with admin
   access and a corresponding ``.pypirc``::

     python3 setup.py sdist upload

6. Create a new github release. Tag and release title are the version number.

7. Finally, change the version number to the next version number with a ``dev``
   tag. Eg: ``0.4.4.dev``. Commit the version change, make a PR, and merge to ``master``.
