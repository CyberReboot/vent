import argparse
import os
import sys
from subprocess import call, check_output, PIPE, Popen

def msg():
    return '''get_logs [-a] ([-c CONTAINER ...] | [-n NAMESPACE ...]) [-f FILE ...]


special option combinations:
    -a -c IMAGE ...                 print logs about all containers built from IMAGE
    -a -n                           print logs about all namespaces
    -c CONTAINER ... -f FILE ...    print logs about FILE in CONTAINER
    -n NAMESPACE ... -f FILE ...    print logs about FILE in NAMESPACE
    '''

def set_parser():
    parser = argparse.ArgumentParser(prog="get_logs", usage=msg())
    parser.add_argument("-a", "--all", help="print all logs, unfiltered", action="store_true")
    parser.add_argument("-f", "--file", help="print logs about uploaded FILE", type=str, nargs="*")
    #-c and -n cannot be used in the same command
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--container", help="print logs about CONTAINER", type=str, nargs="+")
    group.add_argument("-n", "--namespace", help="print logs about NAMESPACE", type=str, nargs="*")
    return parser

def parse_args(args, parser):
    if args.all:
        if args.container:
            for image in args.container:
                print_image_containers(image)
        elif args.namespace == []:
            #get all namespaces
            namespaces = check_output("docker images | grep -v REPOSITORY | awk \"{print \$1}\" | grep / | cut -f1 -d\"/\" | uniq;", shell=True).split("\n")
            del(namespaces[-1])
            print namespaces
            for namespace in namespaces:
                print_namespace(namespace)
        elif args.namespace == args.container == args.file == None:
            print_all_logs()
        else:
            parser.print_help()
            print "get_logs: error: argument -a/--all: expected no arguments, -n/--namespace, or -c/--container IMAGE"
            sys.exit(1)
    elif args.container != None:
        if args.file != [] and args.file != None:
            for container in args.container:
                for file in args.file:
                    print_file_per_container(file, container)
        else:
            for container in args.container:
                print_container(container)
    elif args.namespace != None:
        print "asd"
        if args.namespace == []:
            parser.print_help()
            print "get_logs: error: argument -n/--namespace: expected at least one argument"
            sys.exit(1)
        if args.file != [] and args.file != None:
            for namespace in args.namespace:
                for file in args.file:
                    print_file_per_namespace(file, namespace)
        else:
            for name in args.namespace:
                print_namespace(name)
    elif args.file != None:
        if args.file == []:
            parser.print_help()
            print "get_logs: error: argument -f/--file: expected at least one argument"
            sys.exit(1)
        for file in args.file:
            print_file_log(file)

def print_file_per_container(filename, container):
    os.system("docker logs core-aaa-syslog | grep "+filename+" | grep "+container)
    os.system("docker logs core-aaa-redis | grep "+filename+" | grep "+container)
    os.system("docker logs core-aaa-rabbitmq | grep "+filename+" | grep "+container)
    os.system("docker logs core-rmq-es-connector | grep "+filename+" | grep "+container)

def print_file_per_namespace(filename, namespace):
    os.system("docker logs core-aaa-syslog | grep "+filename+" | grep "+namespace)
    os.system("docker logs core-aaa-redis | grep "+filename+" | grep "+namespace)
    os.system("docker logs core-aaa-rabbitmq | grep "+filename+" | grep "+namespace)
    os.system("docker logs core-rmq-es-connector | grep "+filename+" | grep "+namespace)

def print_container(container):
    os.system("docker logs core-aaa-syslog | grep "+container+"/")
    os.system("docker logs core-aaa-redis | grep "+container+"/")
    os.system("docker logs core-aaa-rabbitmq | grep "+container+"/")
    os.system("docker logs core-rmq-es-connector | grep "+container+"/")

def print_image_containers(image):
    os.system("docker logs core-aaa-syslog | grep "+image+"/")
    os.system("docker logs core-aaa-redis | grep "+image+"/")
    os.system("docker logs core-aaa-rabbitmq | grep "+image+"/")
    os.system("docker logs core-rmq-es-connector | grep "+image+"/")

def print_namespace(namespace):
    os.system("docker logs core-aaa-syslog | grep "+namespace+"/")
    os.system("docker logs core-aaa-redis | grep "+namespace+"/")
    os.system("docker logs core-aaa-rabbitmq | grep "+namespace+"/")
    os.system("docker logs core-rmq-es-connector | grep "+namespace+"/")

def print_file_log(filename):
    os.system("docker logs core-aaa-syslog | grep "+filename)
    os.system("docker logs core-aaa-redis | grep "+filename)
    os.system("docker logs core-aaa-rabbitmq | grep "+filename)
    os.system("docker logs core-rmq-es-connector | grep "+filename)

def print_all_logs():
    os.system("docker logs core-aaa-syslog")
    os.system("docker logs core-aaa-redis")
    os.system("docker logs core-aaa-rabbitmq")
    os.system("docker logs core-rmq-es-connector")

def main():
    parser = set_parser()
    #no args provided, display help text
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    parse_args(parser.parse_args(), parser)

if __name__ == "__main__":
    main()