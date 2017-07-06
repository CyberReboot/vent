#!/bin/sh
if [ ! -f "/var/lib/boot2docker/vent.sh" ]; then
	sudo /usr/local/etc/init.d/openssh stop
	pgrep /usr/local/sbin/sshd | sudo xargs kill -9
	echo $'Match User docker\n\tAllowTCPForwarding no\n\tX11Forwarding no\n\tForceCommand /scripts/wrapper.sh' >> /usr/local/etc/ssh/sshd_config
	sudo /usr/local/etc/init.d/openssh restart
	touch /var/lib/boot2docker/vent.sh
fi
