FROM boot2docker/boot2docker
ADD . $ROOTFS/data/
ADD custom $ROOTFS/etc/rc.d/custom
ADD motd $ROOTFS/etc/motd
RUN echo "built on $(date)" >> $ROOTFS/data/VERSION
RUN echo "echo \"vent \$(cat /data/VERSION)\"" >> $ROOTFS/etc/profile.d/boot2docker.sh
RUN echo "/etc/rc.d/custom" >> $ROOTFS/opt/bootscript.sh

# install dependencies
RUN mkdir -p $ROOTFS/usr/local/share/man/man1
RUN mv $ROOTFS/data/dependencies/tinycore-python2/tce-python/python2.7.1 $ROOTFS/usr/local/share/man/man1/python2.7.1
RUN mv $ROOTFS/data/dependencies/tinycore-python2/tce-python/libpython2.7.so.1.0 $ROOTFS/usr/local/lib/libpython2.7.so.1.0
RUN mv $ROOTFS/data/dependencies/tinycore-python2/tce-python/libpython2.7.so $ROOTFS/usr/local/lib/libpython2.7.so
RUN mv $ROOTFS/data/dependencies/tinycore-python2/tce-python/python-2.7.pc $ROOTFS/usr/local/lib/pkgconfig/python-2.7.pc
RUN mv $ROOTFS/data/dependencies/tinycore-python2/tce-python/python2.7-config $ROOTFS/usr/local/bin/python2.7-config
RUN mv $ROOTFS/data/dependencies/tinycore-python2/tce-python/python2.7 $ROOTFS/usr/local/bin/python2.7
RUN tar xf $ROOTFS/data/dependencies/tinycore-python2/tce-python/python.tar
RUN mv /usr/local/lib/python2.7 $ROOTFS/usr/local/lib/python2.7
RUN tar xf $ROOTFS/data/dependencies/tinycore-python2/tce-python/python-include.tar
RUN mv /usr/local/include/python2.7 $ROOTFS/usr/local/include/python2.7
RUN rm -rf $ROOTFS/data/dependencies

RUN /make_iso.sh
CMD ["cat", "boot2docker.iso"]
