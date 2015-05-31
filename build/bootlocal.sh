#/bin/sh
echo $'Match User docker\n\tAllowTCPForwarding no\n\tX11Forwarding no\n\tForceCommand TERM=xterm LANG=C.UTF-8 /usr/local/bin/python2.7 /data/menu_launcher.py' >> /usr/local/etc/ssh/sshd_config
sleep 10
/usr/local/etc/init.d/openssh stop
/usr/local/etc/init.d/openssh start
# EOF
