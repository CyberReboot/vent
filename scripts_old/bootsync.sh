#!/bin/sh
if [ ! -f "/var/lib/boot2docker/vent.sh" ]; then
	sudo /usr/local/etc/init.d/openssh stop
	pgrep /usr/local/sbin/sshd | sudo xargs kill -9
	mkdir -p /var/lib/docker/data/files
	chmod -R 777 /var/lib/docker/data/files
	ln -s /var/lib/docker/data/files /files
	echo $'Match User docker\n\tAllowTCPForwarding no\n\tX11Forwarding no\n\tForceCommand /scripts/wrapper.sh' >> /usr/local/etc/ssh/sshd_config
	sudo /usr/local/etc/init.d/openssh restart
	# TODO loop through files in info_tools rather than manually doing each one
	sudo ln -s /scripts/info_tools/get_info.sh /usr/local/bin/vent-get-info
	sudo ln -s /scripts/info_tools/get_logs.py /usr/local/bin/vent-get-logs
	sudo ln -s /scripts/info_tools/get_messages.sh /usr/local/bin/vent-get-messages
	sudo ln -s /scripts/info_tools/get_namespaces.py /usr/local/bin/vent-get-namespaces
	sudo ln -s /scripts/info_tools/get_service.sh /usr/local/bin/vent-get-service
	sudo ln -s /scripts/info_tools/get_status.py /usr/local/bin/vent-get-status
	sudo ln -s /scripts/info_tools/get_tasks.sh /usr/local/bin/vent-get-tasks
	sudo ln -s /scripts/info_tools/get_tools.sh /usr/local/bin/vent-get-tools
	sudo ln -s /scripts/info_tools/get_types.sh /usr/local/bin/vent-get-types
	sudo ln -s /scripts/info_tools/get_visualization.sh /usr/local/bin/vent-get-visualization
	sudo ln -s /scripts/vent /usr/local/bin/vent
	sudo ln -s /scripts/vent-generic /usr/local/bin/vent-generic
	if ! [ "$(ls -A /var/lib/docker/data/templates/core)" ]; then
		sudo mv /vent/templates/ /var/lib/docker/data/templates 2>/dev/null
	fi
	if ! [ "$(ls -A /var/lib/docker/data/core)" ]; then
		sudo mv /vent/core/ /var/lib/docker/data/core 2>/dev/null
	fi
	sudo chmod -R 777 /var/lib/docker/data/core
	touch /var/lib/boot2docker/vent.sh
fi
