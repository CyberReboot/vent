#!/bin/bash
########################################################
##### EXPERIMENTAL, USE AT YOUR OWN RISK!!! ############
########################################################

distro_family=$(uname -s 2> /dev/null || echo "unknown")
docker_installed=false
python_installed=false

# check operating system
if [ "$distro_family" = "Linux" ]; then
    # !! TODO
    echo "found Linux..."
    distro_name="unknown"
    distro_version="unknown"
    exit
elif [ "$distro_family" = "Darwin" ]; then
    echo "found Darwin..."

    # check for docker
    if [[ $(which docker) ]]; then
        docker_version="100"
        docker_version_lines=$(docker version | grep Version: | awk '{print $2}')
        while read -r line ; do
            temp_docker_version="$(echo $line | cut -f1,2 -d. )"
            if [[ "$temp_docker_version" < "$docker_version" ]]; then
                docker_version=$temp_docker_version
            fi
        done <<< "$docker_version_lines"
        if [[ "$docker_version" < "1.12" ]]; then
            read -r -p "recommend using Docker >= 1.12.0, but found $docker_version, do you want to continue anyway? [y/N]" response
            case $response in
                [yY][eE][sS]|[yY])
                docker_installed=true
                echo "found Docker..."
                ;;
            *)
                exit
                ;;
            esac
        else
            docker_installed=true
            echo "found Docker..."
        fi
    else
        echo "please install Docker for OSX and then try this installer again."
        exit
    fi

    # check for python
    if [[ $(which python2.7) ]]; then
        python_installed=true
    elif [[ $(which python3) ]]; then
        read -r -p "recommend using Python 2.7.x, do you want to continue anyway? [y/N]" response
        case $response in
            [yY][eE][sS]|[yY])
            echo
            ;;
        *)
            exit
            ;;
        esac
        python_installed=true
    elif [[ $(which python) ]]; then
        read -r -p "recommend using Python 2.7.x, do you want to continue anyway? [y/N]" response
        case $response in
            [yY][eE][sS]|[yY])
            echo
            ;;
        *)
            exit
            ;;
        esac
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
            sudo mkdir -p /vent;
            sudo chmod -R 777 /vent;
            cp -R vent/* /vent/;
            sudo mkdir -p /scripts;
            sudo chmod -R 777 /scripts;
            cp -R scripts/* /scripts/;
            sudo mkdir -p /var/lib/docker;
            /scripts/build.sh;
            sudo /scripts/custom;
            /scripts/vent-cli;
        fi
    fi
else
    echo "Please run as a user with sudo privileges."
fi
