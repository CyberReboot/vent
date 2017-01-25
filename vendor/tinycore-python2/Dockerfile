FROM tatsushid/tinycore:7.2-x86_64

# Instructions are run with 'tc' user

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG=C.UTF-8 LC_ALL=C

#RUN echo 'http://distro.ibiblio.org/tinycorelinux/' > /opt/tcemirror
RUN tce-load -wic gnupg curl \
    && rm -rf /tmp/tce/optional/*

# gpg: key 18ADD4FF: public key "Benjamin Peterson <benjamin@python.org>" imported
RUN gpg2 --keyserver pool.sks-keyservers.net --recv-keys C01E1CAD5EA2C4F0B8E3571504C367C218ADD4FF

ENV PYTHON_VERSION 2.7.13

# if this is called "PIP_VERSION", pip explodes with "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 9.0.1

RUN tce-load -wic \
        bzip2-dev \
        flex \
        file \
        gcc \
        make \
        linux-4.2.1_api_headers \
        glibc_add_lib \
        glibc_base-dev \
        openssl-dev \
        gdbm-dev \
        ncurses-dev \
        readline-dev \
        sqlite3-dev \
        zlib_base-dev \
        tk-dev \
        libX11-dev \
        libXss \
        xorg-proto \
    && cd /tmp \
    && curl -SL "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz" -o python.tar.xz \
    && curl -SL "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz.asc" -o python.tar.xz.asc \
    && gpg2 --verify python.tar.xz.asc \
    && rm python.tar.xz.asc \
    && tar -xJf python.tar.xz \
    && rm python.tar.xz \
    && cd "/tmp/Python-$PYTHON_VERSION" \
    && ./configure --enable-shared --with-ensurepip=install \
    && make \
    && mkdir tmp_install \
    && make install DESTDIR=tmp_install \
    && for F in `find tmp_install | xargs file | grep "executable" | grep ELF | grep "not stripped" | cut -f 1 -d :`; do \
            [ -f $F ] && strip --strip-unneeded $F; \
        done \
    && for F in `find tmp_install | xargs file | grep "shared object" | grep ELF | grep "not stripped" | cut -f 1 -d :`; do \
            [ -f $F ] && if [ ! -w $F ]; then chmod u+w $F && strip -g $F && chmod u-w $F; else strip -g $F; fi \
        done \
    && for F in `find tmp_install | xargs file | grep "current ar archive" | cut -f 1 -d :`; do \
            [ -f $F ] && strip -g $F; \
        done \
    && find tmp_install \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' + \
    && find tmp_install \( -type d -a -name test -o -name tests \) | xargs rm -rf \
    && $(cd tmp_install; sudo cp -R . /) \
    && rm -rf "/tmp/Python-$PYTHON_VERSION" \
    && cd /tmp/tce/optional \
    && for PKG in `ls *-dev.tcz`; do \
            echo "Removing $PKG files"; \
            for F in `unsquashfs -l $PKG | grep squashfs-root | sed -e 's/squashfs-root//'`; do \
                [ -f $F -o -L $F ] && sudo rm -f $F; \
            done; \
            INSTALLED=$(echo -n $PKG | sed -e s/.tcz//); \
            sudo rm -f /usr/local/tce.installed/$INSTALLED; \
        done \
    && for PKG in binutils.tcz \
                cloog.tcz \
                file.tcz \
                flex.tcz \
                gcc.tcz \
                gcc_libs.tcz \
                linux-4.2.1_api_headers.tcz \
                make.tcz \
                sqlite3-bin.tcz \
                xorg-proto.tcz; do \
            echo "Removing $PKG files"; \
            for F in `unsquashfs -l $PKG | grep squashfs-root | sed -e 's/squashfs-root//'`; do \
                [ -f $F -o -L $F ] && sudo rm -f $F; \
            done; \
            INSTALLED=$(echo -n $PKG | sed -e s/.tcz//); \
            sudo rm -f /usr/local/tce.installed/$INSTALLED; \
        done \
    && sudo rm -f /usr/bin/file \
    && sudo /sbin/ldconfig \
    && rm -rf /tmp/tce/optional/* \
    && curl -SL 'https://bootstrap.pypa.io/get-pip.py' | sudo python2 \
    && sudo pip install --no-cache-dir --upgrade pip==$PYTHON_PIP_VERSION \
    && sudo pip install --no-cache-dir docker \
    && sudo pip uninstall -y pip \
    && sudo find /usr/local \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' + \
    && find /usr/local \( -type d -a -name test -o -name tests \) | sudo xargs rm -rf \
    && sudo rm -rf /usr/src/python

# write resulting build to stdout
RUN mkdir /tmp/python2
WORKDIR /tmp/python2
RUN cp -R /usr/local/lib/python2.7 . && tar cf python.tar python2.7 && rm -rf python2.7
RUN cp -R /usr/local/include/python2.7 . && tar cf python-include.tar python2.7 && rm -rf python2.7
RUN cp -R /usr/local/bin/python2.7 .
RUN cp -R /usr/local/bin/python2.7-config .
RUN cp -R /usr/local/lib/libpython2.7.so .
RUN cp -R /usr/local/lib/libpython2.7.so.1.0 .
RUN cp -R /usr/local/lib/pkgconfig/python-2.7.pc .
RUN cp -R /usr/local/share/man/man1/python2.7.1 .
RUN cd /tmp && tar cf python2.tar /tmp/python2
CMD ["cat", "/tmp/python2.tar"]
