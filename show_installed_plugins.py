def get_installed_plugins():
	import os
	try:

	plugins = os.listdir("/var/lib/docker/data/plugin_repos")
	p = {}
        p['title'] = 'Installed Plugins'
        p['type'] = MENU
        p['subtitle'] = 'Installed Plugins:'
        p['options'] = []

        for plugin in plugins:
        	if os.path.isdir("/var/lib/docker/data/plugin_repos/"+plugin
        		p['options'].append({ 'title': plugin, 'type': INFO, 'command': '' })

        return p

    except:
    	pass