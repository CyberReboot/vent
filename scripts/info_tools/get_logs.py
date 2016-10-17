#!/usr/bin/env python2.7

import argparse
import os
import sys
from subprocess import call, check_output, PIPE, Popen

def msg():
    """custom message for --help"""
    return '''get_logs [-a] ([-c CONTAINER ...] | [-n NAMESPACE ...]) [-f FILE ...]


special option combinations:
    -a -c IMAGE ...                 print logs about all containers built from IMAGE
    -a -n                           print logs about all namespaces
    -c CONTAINER ... -f FILE ...    print logs about FILE in CONTAINER
    -n NAMESPACE ... -f FILE ...    print logs about FILE in NAMESPACE
    '''

def set_parser():
    """initialize parser"""
    parser = argparse.ArgumentParser(prog="get_logs", usage=msg())
    parser.add_argument("-a", "--all", help="print all logs, unfiltered", action="store_true")
    parser.add_argument("-f", "--file", help="print logs about uploaded FILE", type=str, nargs="*")
    #-c and -n cannot be used in the same command
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--container", help="print logs about CONTAINER", type=str, nargs="+")
    group.add_argument("-n", "--namespace", help="print logs about NAMESPACE", type=str, nargs="*")
    return parser

def parse_args(args, parser):
    """parse arguments, calls correct print functions based on arguments"""
    #checks if each container with logs exist. Removes from list if it doesn't
    cores = ["core-aaa-syslog", "core-aaa-redis", "core-aaa-rabbitmq", "core-rmq-es-connector", "vent-management"]
    updated_cores = []
    for core in cores:
        exists = check_output("docker ps | grep "+core+" | tee", shell=True)
        if core in exists:
            updated_cores.append(core)
    cores = updated_cores
    if args.all:
        #-a -c IMAGE
        if args.container:
            for image in args.container:
                print_image_containers(image, cores)
        #-a -n
        elif args.namespace == []:
            #get all namespaces
            namespaces = check_output("docker images | grep -v REPOSITORY | awk \"{print \$1}\" | grep / | cut -f1 -d\"/\" | sort | uniq;", shell=True).split("\n")
            del(namespaces[-1])
            for namespace in namespaces:
                print_namespace(namespace, cores)
        #-a
        elif args.namespace == args.container == args.file == None:
            print_all_logs(cores)
        else:
            parser.print_help()
            print("get_logs: error: argument -a/--all: expected no arguments, -n/--namespace, or -c/--container IMAGE")
            return
    elif args.container != None:
        #-c CONTAINER -f FILE
        if args.file != [] and args.file != None:
            for container in args.container:
                for file in args.file:
                    print_file_per_container(file, container, cores)
        #-c CONTAINER
        else:
            for container in args.container:
                print_container(container, cores)
    elif args.namespace != None:
        if args.namespace == []:
            parser.print_help()
            print("get_logs: error: argument -n/--namespace: expected at least one argument")
            return
        #-n NAMESPACE -f FILE
        if args.file != [] and args.file != None:
            for namespace in args.namespace:
                for f in args.file:
                    print_file_per_namespace(f, namespace, cores)
        #-n NAMESPACE
        else:
            for name in args.namespace:
                print_namespace(name, cores)
    elif args.file != None:
        if args.file == []:
            parser.print_help()
            print("get_logs: error: argument -f/--file: expected at least one argument")
            return
        #-f FILE
        for f in args.file:
            print_file_log(f, cores)

def print_file_per_container(filename, container, cores):
    """print logs for each container that processed each file"""
    for core in cores:
        os.system("docker logs "+core+" | grep "+filename+" | grep "+container+" | tee")

def print_file_per_namespace(filename, namespace, cores):
    """proint logs for all containers in each namespace that processed each file"""
    for core in cores:
        os.system("docker logs "+core+" | grep "+filename+" | grep "+namespace+" | tee")

def print_container(container, cores):
    """print logs for each container"""
    for core in cores:
        if container == core:
            print(container)
            os.system("docker logs "+container)
        os.system("docker logs "+core+" | grep "+container+"/ | tee")

def print_image_containers(image, cores):
    """print logs for all container built from each container"""
    for core in cores:
        os.system("docker logs "+core+" | grep "+image+"/ | tee")

def print_namespace(namespace, cores):
    """print logs for all containers in each namespace"""
    for core in cores:
        if namespace == "core" and core != "vent-management":
            os.system("docker logs "+core)
        os.system("docker logs "+core+" | grep "+namespace+"/ | tee")

def print_file_log(filename, cores):
    """print logs for each file"""
    for core in cores:
        os.system("docker logs "+core+" | grep "+filename+" | tee")

def print_all_logs(cores):
    """print all logs"""
    for core in cores:
        os.system("docker logs "+core)

def main(args):
    parser = set_parser()
    #no args provided, display help text
    if len(args) == 1:
        parser.print_help()
    else:
        parse_args(parser.parse_args(), parser)
    return

if __name__ == "__main__":
    args = sys.argv
    main(args)
