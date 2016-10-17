#!/bin/bash

# TODO check distro
# TODO check if docker is already installed, and check version
# TODO check that python is installed and which version
distro_family=$(uname -s 2> /dev/null || echo "unknown")
docker_installed=false
python_installed=false

# check operating system
if [ "$distro_family" = "Linux" ]; then
    echo "found Linux..."
    distro_name="unknown"
    distro_version="unknown"
    exit
elif [ "$distro_family" = "Darwin" ]; then
    echo "found Darwin..."

    # check for docker
    if [[ $(which docker) ]]; then
        echo "$(docker version)"
        echo "recommend using Docker >= 1.12.0, do you want to continue anyway?"
        # TODO
        docker_installed=true
    else
        echo "please install Docker for OSX and then try this installer again."
        exit
    fi

    # check for python
    if [[ $(which python2.7) ]]; then
        python_installed=true
    elif [[ $(which python3) ]]; then
        echo "recommend using Python 2.7.x, do you want to continue anyway?"
        # TODO
        python_installed=true
    elif [[ $(which python) ]]; then
        echo "$(python -V)"
        # TODO
        echo "recommend using Python 2.7.x, do you want to continue anyway?"
        python_installed=true
    fi

    # check 
    if [ "$python_installed" = true ]; then
        echo "python installed"
    else
        echo "please install Python 2.7 for OSX and then try this installer again."
        exit
    fi
else
    echo "unsupported operating system, exiting."
    exit
fi

CAN_I_RUN_SUDO=$(sudo -n uptime 2>&1|grep "load"|wc -l)
if [ ${CAN_I_RUN_SUDO} -gt 0 ]; then
    if [ "$python_installed" = true ]; then
        if [ "$docker_installed" = true ]; then
            sudo mkdir /vent;
            sudo chmod -R 777 /vent;
            cp -R * /vent/;
            sudo mkdir /var/lib/docker;
            cd /vent && ./build.sh;
            sudo /vent/custom;
            vent-cli;
        fi
    fi
else
    echo "Please run as a user with sudo privileges."
fi

exit

#    sudo apt-get update;
#    sudo apt-get install -y apt-transport-https ca-certificates python2.7;
#    sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D;
#    sudo bash -c 'echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" > /etc/apt/sources.list.d/docker.list';
#    sudo apt-get update;
#    sudo apt-get purge lxc-docker;
#    sudo apt-get install -y linux-image-extra-$(uname -r) linux-image-extra-virtual;
#    sudo apt-get install -y docker-engine;
#    sudo service docker start;
#    sudo groupadd docker;
#    sudo usermod -aG docker $USER;

#bash -c 'python2.7 /vent/menu_launcher.py';
