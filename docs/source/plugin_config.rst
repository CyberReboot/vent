Filling in Custom Configurations of Plugins
###########################################

Say your custom plugin, called ``example_plugin``, has a 
``example_plugin.config`` file that it needs filled out before the plugin is 
built into an image. 

.. code-block:: bash
   :caption: example_plugin.config
   
   [Some_Section]
   example_option1 = FILL IN
   example_option2 = FILL IN
   example_option3 = FILL IN

Vent can now fill in those values for you. 
In your home directory, have a file called ``.plugin_config.yml``. 

We'll fill in ``.plugin_config.yml`` with the necessary fields:

.. code-block:: bash
   :caption: .plugin.config.yml

   example_plugin
       Some_Section: 
           example_option1 = 1
           example_option2 = 2
           example_option3 = 3

Vent will assume that, in the directory ``example_plugin``, there exists another
directory titled ``config`` that has the actual config file.
The path of our example would be
``example_plugin/config/example_plugin.config``. 

Using this ``.plugin_config.yml``, you can fill in multiple tools' config files
at the same time. 

If you make a change to your config files and want to rebuild the images using
these new settings, *clean* and then *build* the plugin tools in the ``plugins`` 
submenu. Vent will fill in the config files with the new values.
