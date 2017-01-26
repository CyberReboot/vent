import json
import os

from vent.api.plugins import Plugin
from vent.api.templates import Template
from vent.helpers.meta import Version

class Action:
   """ Handle actions in menu """
   def __init__(self, **kargs):
       self.plugin = Plugin(**kargs)

   def add(self, repo, tools=None, overrides=None, version="HEAD",
           branch="master", build=True, user=None, pw=None, group=None,
           version_alias=None, wild=None, remove_old=True, disable_old=True):
       """ Add a new set of tool(s) """
       status = (True, None)
       status = self.plugin.add(repo,
                                tools=tools,
                                overrides=overrides,
                                version=version,
                                branch=branch,
                                build=build,
                                user=user,
                                pw=pw,
                                group=group,
                                version_alias=version_alias,
                                wild=wild,
                                remove_old=remove_old,
                                disable_old=disable_old)
       return status

   @staticmethod
   def remove():
       return

   def start(self,
             repo=None,
             name=None,
             group=None,
             enabled="yes",
             branch="master",
             version="HEAD"):
       """
       Start a set of tools that match the parameters given, if no parameters
       are given, start all installed tools on the master branch at verison
       HEAD that are enabled
       """
       args = locals()
       options = ['name',
                  'namespace',
                  'built',
                  'path',
                  'image_name',
                  'branch',
                  'version']
       status = (True, None)
       sections, template = self.plugin.constraint_options(args, options)
       for section in sections:
           # ensure tools are built before starting them
           if not sections[section]['built'] == 'yes':
               # try and build the tool first
               status = self.build(name=sections[section]['name'],
                                   group=group,
                                   enabled=enabled,
                                   branch=branch,
                                   version=version)

           # only start tools that have been built
           if sections[section]['built'] == 'yes':
               # initialize needed vars
               tool_dict = {}
               template_path = os.path.join(sections[section]['path'], 'vent.template')
               container_name = sections[section]['image_name'].replace(':','-')
               image_name = sections[section]['image_name']

               # checkout the right version and branch of the repo
               self.plugin.branch = branch
               self.plugin.version = version
               cwd = os.getcwd()
               os.chdir(os.path.join(sections[section]['path']))
               status = self.plugin.checkout()
               os.chdir(cwd)

               # set docker settings for container
               vent_template = Template(template_path)
               status = vent_template.section('docker')
               tool_dict[container_name] = {'Image':image_name}
               if status[0]:
                   # !! TODO check vent.template files for runtime dependencies (links, etc.)
                   # !! TODO link to rabbitmq container for plugin containers
                   for option in status[1]:
                       tool_dict[container_name][option[0]] = option[1]

                   # add extra labels
                   if 'Labels' not in tool_dict[container_name]:
                       tool_dict[container_name]['Labels'] = {}
                   tool_dict[container_name]['Labels']['vent'] = Version()
                   tool_dict[container_name]['Labels']['vent.groups'] = '' # TODO
                   tool_dict[container_name]['Labels']['vent.namespace'] = sections[section]['namespace']
                   tool_dict[container_name]['Labels']['vent.branch'] = branch
                   tool_dict[container_name]['Labels']['vent.version'] = version
                   tool_dict[container_name]['Labels']['vent.name'] = sections[section]['name']

           # write out container configurations to be started by vent-management
           with open('/tmp/vent_start.txt', 'a') as f:
               json.dump(tool_dict, f)
               f.write("|")
               if 'groups' in sections[section] and 'core' in sections[section]['groups']:
                   f.write("0")
               else:
                   f.write("1")
               f.write("\n")
       return status

   @staticmethod
   def stop():
       return

   @staticmethod
   def clean():
       return

   def build(self,
             repo=None,
             name=None,
             group=None,
             enabled="yes",
             branch="master",
             version="HEAD"):
       """ Build a set of tools that match the parameters given """
       args = locals()
       options = ['image_name', 'path']
       status = (True, None)
       self.plugin.build = True
       self.plugin.branch = branch
       self.plugin.version = version
       sections, template = self.plugin.constraint_options(args, options)
       for section in sections:
           os.chdir(sections[section]['path'])
           status = self.plugin.checkout()
           if status[0]:
               template = self.plugin.build_image(template,
                                                  sections[section]['path'],
                                                  sections[section]['image_name'],
                                                  section)
       template.write_config()
       return status

   @staticmethod
   def backup():
       return

   @staticmethod
   def restore():
       return

   @staticmethod
   def show():
       # repos, core, tools, images, built, running, etc.
       return

   @staticmethod
   def configure():
       # tools, core, etc.
       return

   @staticmethod
   def system_info():
       return

   @staticmethod
   def system_conf():
       return

   @staticmethod
   def system_commands():
       # restart, shutdown, upgrade, etc.
       return

   @staticmethod
   def logs():
       return

   @staticmethod
   def help():
       return
