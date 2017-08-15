Vent Quickstart Guide
#####################

Getting Vent set up is quick and easy.

**1.** First, use pip to install the latest *stable* version of Vent:

   - Using pip::

       pip install vent && vent


   Developer versions of Vent are available but may not be entirely stable.

   - Using Docker::

       docker pull cyberreboot/vent
       docker run -it vent_image_id

   - Using Git::

       git clone https://github.com/CyberReboot/vent
       cd vent && make && vent

**2.** Now that Vent has started, let's add, build, and start the core tools.

   1. In the main menu, press ``^X`` to open the action menu
   2. Select ``Core Tools`` or press ``c``
   3. Select ``Add all latest core tools`` or press ``i``. Vent will now clone the
      core tools' directories from `CyberReboot/vent`_.
   4. Select ``Build core tools`` from the core tools sub-menu and use the arrow
      keys and the Enter key to press ``OK``. It's possible to choose which core
      tools are built using the Space key. Boxes with an ``X`` in them have been
      selected. Note that building the core tools takes a few minutes. Please
      be patient while Vent creates the images.
   5. Once the tool images are built, go back to the core tools sub-menu from
      main action menu and select ``Start core tools`` and hit ``OK``. Much like
      ``Build core tools``, it's possible to select which core tools are
      started.

.. _CyberReboot/vent: https://github.com/CyberReboot/vent/

**3.** The core tools' containers are up and running. Next, let's add some plugins.

   1. From the action menu, Select ``Plugins`` or press ``p``.
   2. Select ``Add new plugin`` or press ``a``.
   3. For this quick start guide, we will use one of the example plugins
      provided from `CyberReboot/vent-plugins`_. So just hit ``OK`` on the form.
   4. Press the Space key to choose the ``master`` branch and hit ``OK``.
   5. Uncheck all the boxes except for ``/tcpdump_hex_parser`` and hit ``OK``.
      Depending on the plugin, add times may vary so it is not unusual for long
      plugin add times.

.. _CyberReboot/vent-plugins: https://github.com/CyberReboot/vent-plugins/

**4.** Now we have a plugin that can process files with the extension ``.pcap``.

   1. Now, at the Vent main menu, look for the field ``File Drop``. This is the
      folder that Vent watches for new files. By default, the path is
      ``/tmp/user_name/vent_files``
   2. Move or copy a ``.pcap`` file into the path. Vent will recognize this new file
      and start ``tcpdump_hex_parser``. Depending on the size of the ``.pcap``
      file, it could take anywhere from a few seconds to minutes.

Congrats! Vent is setup and has successfully recognized the pcap file and ran a
plugin that specifically deals with pcaps.


