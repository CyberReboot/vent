#/bin/sh
echo $'Match User docker\n\tAllowTCPForwarding no\n\tX11Forwarding no\n\tForceCommand /data/wrapper.sh' >> /usr/local/etc/ssh/sshd_config
sleep 10
/usr/local/etc/init.d/openssh stop
/usr/local/etc/init.d/openssh start
# EOF
