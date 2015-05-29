FROM boot2docker/boot2docker
ADD . $ROOTFS/data/
ADD custom $ROOTFS/etc/rc.d/custom
ADD motd $ROOTFS/etc/motd
RUN echo "built on $(date)" >> $ROOTFS/data/VERSION
RUN echo "echo \"vent \$(cat /data/VERSION)\"" >> $ROOTFS/etc/profile.d/boot2docker.sh
RUN echo "/etc/rc.d/custom" >> $ROOTFS/opt/bootscript.sh
RUN /make_iso.sh
CMD ["cat", "boot2docker.iso"]
