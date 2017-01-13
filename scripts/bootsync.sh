#!/bin/sh
if [ ! -f "/var/lib/boot2docker/vent.sh" ]; then
	sudo /usr/local/etc/init.d/openssh stop
	pgrep /usr/local/sbin/sshd | sudo xargs kill -9
	echo $'Match User docker\n\tAllowTCPForwarding no\n\tX11Forwarding no\n\tForceCommand /scripts/wrapper.sh' >> /usr/local/etc/ssh/sshd_config
	sudo /usr/local/etc/init.d/openssh restart
	mkdir -p /var/lib/docker/data/files
	mkdir -p /var/lib/docker/data/plugins
	mkdir -p /var/lib/docker/data/core
	ln -s /var/lib/docker/data/files /files
	sudo ln -s /scripts/vent /usr/local/bin/vent
	sudo ln -s /scripts/vent-generic /usr/local/bin/vent-generic
	if ! [ "$(ls -A /var/lib/docker/data/core)" ]; then
		sudo mv /vent/core /var/lib/docker/data/ 2>/dev/null
	fi
	sudo chmod -R 777 /var/lib/docker/data
	touch /var/lib/boot2docker/vent.sh
fi
