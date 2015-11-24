#!/bin/sh
if [ ! -f "/var/lib/boot2docker/vent.sh" ]; then
	sudo /usr/local/etc/init.d/openssh stop
	pgrep /usr/local/sbin/sshd | sudo xargs kill -9
	# TODO probably should ensure that's actually always the mount point
	mkdir -p /mnt/sda1/pcaps
	chmod -R 777 /mnt/sda1/pcaps
	ln -s /mnt/sda1/pcaps /pcaps
	mv /data/profile /var/lib/boot2docker/profile
	echo $'Match User docker\n\tAllowTCPForwarding no\n\tX11Forwarding no\n\tForceCommand /data/wrapper.sh' >> /usr/local/etc/ssh/sshd_config
	sudo /usr/local/etc/init.d/openssh restart
	touch /var/lib/boot2docker/vent.sh
fi

