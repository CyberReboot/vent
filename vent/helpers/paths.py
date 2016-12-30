class PathDirs:
    """ Global path directories for vent """
    def __init__(self,
                 base_dir="/var/lib/docker/data/",
                 collectors_dir="collectors",
                 core_dir="core",
                 plugins_dir="plugins/",
                 plugin_repos="plugin_repos",
                 template_dir="templates/",
                 vis_dir="visualization",
                 info_dir="info_tools/",
                 vent_dir="/vent/",
                 data_dir="/vent/",
                 vendor_dir="/vendor/",
                 scripts_dir="/scripts/"):
        self.base_dir = base_dir
        self.collectors_dir = base_dir + collectors_dir
        self.core_dir = base_dir + core_dir
        self.plugins_dir = base_dir + plugins_dir
        self.plugin_repos = base_dir + plugin_repos
        self.template_dir = base_dir + template_dir
        self.vis_dir = base_dir + vis_dir
        self.scripts_dir = scripts_dir
        self.info_dir = scripts_dir + info_dir
        self.vent_dir = vent_dir
        self.data_dir = data_dir
        self.vendor_dir = vendor_dir
