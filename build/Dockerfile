FROM boot2docker/boot2docker
ADD . $ROOTFS/data/
ADD custom $ROOTFS/etc/rc.d/custom
RUN echo "/etc/rc.d/custom" >> $ROOTFS/opt/bootscript.sh
RUN /make_iso.sh
CMD ["cat", "boot2docker.iso"]
