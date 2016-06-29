
#vent instance name
docker info | grep "Name: "
echo;

#vent instance version
echo -n "Version: ";
cat /data/VERSION | grep -v built
echo;

#date of vent instance creation
cat /data/VERSION | grep built
echo;

#uptime of current vent instance
echo -n "Uptime: ";
uptime | awk "{print \$1}"
echo;


#list of installed plugins
echo "Installed Plugins: ";
docker images | grep / | grep -v core | grep -v collectors | grep -v visualization | awk "{print \$1}";
echo;

#number of images
echo -n "Number of ";
docker info | grep Images:;
echo;

#number of running containers
echo -n "Number of Containers";
docker info | grep Running:;
echo;

#number of stopped containers
echo -n "Number of Containers";
docker info | grep Stopped:;
echo;

#list of active SSH sessions into this vent instance
echo "Active SSH Sessions into this Vent instance: ";
who;
echo;

#verbose
if [ "$1" == "-v" ] 
	then
		#list installed images
		echo "Installed Images: ";
		docker images | grep -v REPOSITORY | awk "{print \$1}";
		echo;

		#list all built containers (running and stopped)
		echo "Containers: ";
		docker ps -a --format 'table {{.Names}} \t {{.Status}}';
fi