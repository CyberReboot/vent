#!/bin/sh
if [ ! -f "/var/lib/boot2docker/vent.sh" ]; then
	sudo /usr/local/etc/init.d/openssh stop
	pgrep /usr/local/sbin/sshd | sudo xargs kill -9
	# TODO probably should ensure that's actually always the mount point
	mkdir -p /var/lib/docker/data/pcaps
	chmod -R 777 /var/lib/docker/data/pcaps
	ln -s /var/lib/docker/data/pcaps /pcaps
	mv /data/profile /var/lib/boot2docker/profile
	echo $'Match User docker\n\tAllowTCPForwarding no\n\tX11Forwarding no\n\tForceCommand /data/wrapper.sh' >> /usr/local/etc/ssh/sshd_config
	sudo /usr/local/etc/init.d/openssh restart
	touch /var/lib/boot2docker/vent.sh
fi

