#!/bin/sh
if [ ! -f "/var/lib/boot2docker/vent.sh" ]; then
	sudo /usr/local/etc/init.d/openssh stop
	pgrep /usr/local/sbin/sshd | sudo xargs kill -9
	mkdir -p /var/lib/docker/data/files
	chmod -R 777 /var/lib/docker/data/files
	ln -s /var/lib/docker/data/files /files
	mv /data/profile /var/lib/boot2docker/profile
	echo $'Match User docker\n\tAllowTCPForwarding no\n\tX11Forwarding no\n\tForceCommand /data/wrapper.sh' >> /usr/local/etc/ssh/sshd_config
	sudo /usr/local/etc/init.d/openssh restart
	touch /var/lib/boot2docker/vent.sh
    sudo ln -s /data/info_tools/get_info.sh /usr/local/bin/vent_get_info
    sudo ln -s /data/info_tools/get_logs.py /usr/local/bin/vent_get_logs
    sudo ln -s /data/info_tools/get_messages.sh /usr/local/bin/vent_get_messages
    sudo ln -s /data/info_tools/get_namespaces.py /usr/local/bin/vent_get_namespaces
    sudo ln -s /data/info_tools/get_service.sh /usr/local/bin/vent_get_service
    sudo ln -s /data/info_tools/get_status.py /usr/local/bin/vent_get_status
    sudo ln -s /data/info_tools/get_tasks.sh /usr/local/bin/vent_get_tasks
    sudo ln -s /data/info_tools/get_tools.sh /usr/local/bin/vent_get_tools
    sudo ln -s /data/info_tools/get_types.sh /usr/local/bin/vent_get_types
fi

