from datetime import datetime

import docker

from vent.helpers.logs import Logger
from vent.helpers.templates import Template


class Image:

    def __init__(self, manifest):
        self.manifest = manifest
        self.d_client = docker.from_env()
        self.logger = Logger(__name__)

    def add(self, image, link_name, tag=None, registry=None, groups=None):
        status = (True, None)
        try:
            pull_name = image
            org = ''
            name = image
            if '/' in image:
                org, name = image.split('/')
            else:
                org = 'official'
            if not tag:
                tag = 'latest'
            if not registry:
                registry = 'docker.io'
            if not link_name:
                link_name = name
            if not groups:
                groups = ''
            full_image = registry + '/' + image + ':' + tag
            image = self.d_client.images.pull(full_image)
            section = ':'.join([registry, org, name, '', tag])
            namespace = org + '/' + name

            # set template section and options for tool at version and branch
            template = Template(template=self.manifest)
            template.add_section(section)
            template.set_option(section, 'name', name)
            template.set_option(section, 'pull_name', pull_name)
            template.set_option(section, 'namespace', namespace)
            template.set_option(section, 'path', '')
            template.set_option(section, 'repo', registry + '/' + org)
            template.set_option(section, 'branch', '')
            template.set_option(section, 'version', tag)
            template.set_option(section, 'last_updated',
                                str(datetime.utcnow()) + ' UTC')
            template.set_option(section, 'image_name',
                                image.attrs['RepoTags'][0])
            template.set_option(section, 'type', 'registry')
            template.set_option(section, 'link_name', link_name)
            template.set_option(section, 'commit_id', '')
            template.set_option(section, 'built', 'yes')
            template.set_option(section, 'image_id',
                                image.attrs['Id'].split(':')[1][:12])
            template.set_option(section, 'groups', groups)

            # write out configuration to the manifest file
            template.write_config()
            status = (True, 'Successfully added ' + full_image)
        except Exception as e:  # pragma: no cover
            self.logger.error(
                'Failed to add image because: {0}'.format(str(e)))
            status = (False, str(e))
        return status

    def update(self, image):
        # TODO
        return
