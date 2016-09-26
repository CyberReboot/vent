#!/bin/sh


# !! TODO need to have a section that shows the supported mime types based on
#         the plugins installed

name=false
version=false
build_date=false
upt=false
installed_plugins=false
num_plugins=false
num_images=false
num_run_containers=false
num_stop_containers=false
num_repos=false
active_ssh=false
installed_images=false
installed_containers=false
installed_repos=false
verbose=false
nics=false
# help flag
help_text(){
echo "Usage:    $(basename "$0")
          $(basename "$0") COMMAND
          $(basename "$0") COMMAND OPTION
          $(basename "$0") all -v
          $(basename "$0") -h

Print information about Vent

$(basename "$0") (no args) - Instance name, version,
build date, uptime, and list installed plugins

Flags:
    -h  Show this help text
    -v  Verbose (only with 'all')

Commands:
    all         All information except installed images and containers
    name        Name of vent instance
    count       Number of installed plugins, images, and containers
    ssh         Active ssh sessions
    installed   Installed plugins, images, and containers
    nics        Network interfaces and ip addresses

Options:
    COMMAND     OPTION          Description
    count       plugins         Number of installed plugins
    count       images          Number of installed images
    count       containers      Number of built containers
    count       repositories    Number of installed plugin repositories
    installed   plugins         List installed plugins
    installed   images          List installed images
    installed   containers      List build containers and their status
    installed   repositories    List installed plugin repositories"
}

for i in "$@"; do
    if [ "$i" = "-h" ] || [ "$i" = "--help" ]; then
        help_text
        exit 0
    fi
    if [ "$i" = "-v" ]; then
        verbose=true
    fi
done

# parse args to print desired information
if [ "$#" -eq 0 ]; then
    name=true
    version=true
    build_date=true
    upt=true
    installed_plugins=true
    nics=true
elif [ "$1" = "all" ]; then
    name=true
    version=true
    build_date=true
    upt=true
    installed_plugins=true
    num_plugins=true
    num_images=true
    num_run_containers=true
    num_stop_containers=true
    num_repos=true
    active_ssh=true
    nics=true
    if [ "$verbose" = true ]; then
        installed_images=true
        installed_containers=true
    fi
elif [ "$1" = "name" ]; then
    name=true
elif [ "$1" = "count" ]; then
    if [ "$#" -eq 2 ]; then
        if [ "$2" = "plugins" ]; then
            num_plugins=true
        elif [ "$2" = "images" ]; then
            num_images=true
        elif [ "$2" = "containers" ]; then
            num_run_containers=true
            num_stop_containers=true
        elif [ "$2" = "repositories" ]; then
            num_repos=true
        fi
    else
        num_plugins=true
        num_images=true
        num_run_containers=true
        num_stop_containers=true
        num_repos=true
    fi
elif [ "$1" = "ssh" ]; then
    active_ssh=true
elif [ "$1" = "installed" ]; then
    if [ "$#" -eq 2 ]; then
        if [ "$2" = "images" ]; then
            installed_images=true
        elif [ "$2" = "containers" ]; then
            installed_containers=true
        elif [ "$2" = "plugins" ]; then
            installed_plugins=true
        elif [ "$2" = "repositories" ]; then
            installed_repos=true
        fi
    else
        installed_plugins=true
        installed_images=true
        installed_containers=true
        installed_repos=true
    fi
elif [ "$1" = "nics" ]; then
    nics=true
else
    echo "Wrong arguments!"
    help_text
fi

# vent instance name
if [ "$name" = true ]; then
    docker info | grep "Name: "
fi

# vent instance version
if [ "$version" = true ]; then
    echo -n "Version: ";
    cat /vent/VERSION | grep -v built
fi

# date of vent instance creation
if [ "$build_date" = true ]; then
    cat /vent/VERSION | grep built
fi

# uptime of current vent instance
if [ "$upt" = true ]; then
    echo -n "Uptime: ";
    uptime | awk "{print \$1}"
    echo;
fi

# number of installed plugins
if [ "$num_plugins" = true ]; then 
    echo -n "Number of Plugins: "
    docker images | grep / | grep -v core | grep -v collectors | grep -v visualization | wc -l;
fi


# number of images
if [ "$num_images" = true ]; then
    echo -n "Number of Images: ";
    docker images | grep -v -c CONTAINERS;
fi

# number of running containers
if [ "$num_run_containers" = true ]; then
    echo -n "Number of Containers";
    docker info | grep Running:;
fi

# number of stopped containers
if [ "$num_stop_containers" = true ]; then
    echo -n "Number of Containers";
    docker info | grep Stopped:;
fi

# number of installed plugin repositories
if [ "$num_repos" = true ]; then
    if [ "$verbose" = true ]; then
        echo -n "Number of Plugin Repositories:";
    fi
    ls /var/lib/docker/data/plugin_repos | wc -w
    echo;
fi

# list of active SSH sessions into this vent instance
if [ "$active_ssh" = true ]; then
    echo "Active SSH Sessions into this Vent instance: ";
    who;
    echo;
fi

# list installed plugins
if [ "$installed_plugins" = true ]; then
    echo "Installed Plugins: ";
    docker images | grep / | grep -v core | grep -v collectors | grep -v visualization | awk "{print \$1}";
    echo;
fi

# list installed images
if [ "$installed_images" = true ]; then
    echo "Installed Images: ";
    docker images | grep -v REPOSITORY | awk "{print \$1}";
    echo;
fi

# list all built containers (running and stopped)
if [ "$installed_containers" = true ]; then
    echo "Built Containers: ";
    docker ps -a --format 'table {{.Names}} \t {{.Status}}';
    echo;
fi

# list installed plugin repositories
if [ "$installed_repos" = true ]; then
    if [ "$verbose" = true ]; then
        echo "Installed Plugin Repositories:";
    fi
    sentence=$(ls /var/lib/docker/data/plugin_repos)
    for word in $sentence
    do
        echo $word;
    done
fi

# list global network interfaces and their ip addresses
if [ "$nics" = true ]; then
    echo "Active Network Interfaces: ";
    ip -o addr show up scope global | while read -r num dev fam addr rest; do echo ${dev}:${addr%/*}; done;
    echo;
fi
