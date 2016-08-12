#!/bin/sh

arg_a=false
arg_h=false
arg_j=false
arg_n=false
arg_r=false
arg_invalid=false

help_text(){
    echo "Usage: $(basename "$0") PARAMETER [Flags..]

Display a live stream of docker resource usage statistics for container(s)

Parameter:
    -a, --all           All stats about all docker containers
    -r, --running       Stats about all running containers
Flags:
    -h, --help          Show this help text
    -j, --json          Print the result as JSON
    -n, --no-stream     Disable streaming stats and only pull first result"
}

echo "Service Stats: CTRL+c to Exit"
echo "loading..."
echo

# Check for minimum number of arguments
if [ $# -lt 1 ]; then
    echo "Invalid use. Not enough arguments."
    help_text
    exit 1;
fi

# Parse arguments
for arg in "$@"; do
    case $arg in
        -a|--all)
        arg_a=true;;

        -h|--help)
        arg_h=true;;

        -j|--json)
        arg_j=true;;

        -n|--no-stream)
        arg_n=true;;

        -r|--running)
        arg_r=true;;

        *) # something else was passed in
        arg_invalid=true
        break;;
    esac
done

# Check for invalid arguments
if [ "$arg_invalid" = true ]; then
    echo "Invalid use. The provided argument(s) is not recognized."
    help_text
    exit 1;
fi

# Check for help
if [ "$arg_h" = true ]; then
    help_text
    exit 0;
fi

# Check for all; this checks for all & running (conflict)
if [ "$arg_a" = true ]; then
    # check if -a and -r
    if [ "$arg_r" = true ]; then
        echo "Invalid use. All and Running are mutually exclusive."
        help_text
        exit 1;
    fi
    # check if -a, -j, -n
    if [ "$arg_j" = true ]; then
        if [ "$arg_n" = true ]; then
            # return all, no-stream, as json
            docker ps -a | awk '{print $NF}' | grep -v NAMES | xargs -I % curl --unix-socket /var/run/docker.sock http:/containers/%/stats?stream=0
            exit 0;
        else
            # return all, with stream, as json
            docker ps -a | awk '{print $NF}' | grep -v NAMES | xargs -I % curl --unix-socket /var/run/docker.sock http:/containers/%/stats?stream=1
            exit 0;
        fi
    # check if -a, -n (-j already ruled out)
    elif [ "$arg_n" = true ]; then
        # return all, with no-stream, no json
        docker ps -a | awk '{print $NF}' | grep -v NAMES | xargs docker stats --no-stream
        exit 0;
    # just -a
    else
        # return all, with stream, no json
        docker ps -a | awk '{print $NF}' | grep -v NAMES | xargs docker stats
        exit 0;
    fi
fi

# Check for running; note running & all already checked above
if [ "$arg_r" = true ]; then
    # check if -r, -j, -n
    if [ "$arg_j" = true ]; then
        if [ "$arg_n" = true ]; then
            # return running, no-stream, as json
            docker ps | awk '{print $NF}' | grep -v NAMES | xargs -I % curl --unix-socket /var/run/docker.sock http:/containers/%/stats?stream=0
            exit 0;
        else
            # return running, with stream, as json
            docker ps | awk '{print $NF}' | grep -v NAMES | xargs -I % curl --unix-socket /var/run/docker.sock http:/containers/%/stats?stream=1
            exit 0;
        fi
    # check if -r, -n (-j already ruled out)
    elif [ "$arg_n" = true ]; then
        # return running, with stream, no json
        docker ps | awk '{print $NF}' | grep -v NAMES | xargs docker stats --no-stream
        exit 0;
    # just -r
    else
        # return running, no stream, no json
        docker ps | awk '{print $NF}' | grep -v NAMES | xargs docker stats
        exit 0;
    fi
fi

# Check if j/n is true; if so, then it was used alone
if [ "$arg_j" = true ] || [ "$arg_n" = true ]; then
    echo "Invalid use. -j/-n are not valid alone; see PARAMETERS."
    help_text
    exit 1;
fi

# Should never make it here
echo "Something went wrong...Please double check your usage."
help_text
exit 1;
