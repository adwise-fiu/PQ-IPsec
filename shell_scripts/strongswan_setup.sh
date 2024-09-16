#!/bin/bash
# Modified from Andreas Steffen's pq-strongswan dockerfile
# (https://github.com/strongX509/docker/blob/master/pq-strongswan/Dockerfile)
VERSION="6.0.0beta6"
LIBOQS_VERSION="0.9.2"

# install packages
DEV_PACKAGES="wget unzip bzip2 make gcc libssl-dev cmake ninja-build" && \
apt-get -y update && \
apt-get -y install iproute2 iputils-ping nano pkg-config $DEV_PACKAGES && \
\
# download and build liboqs
mkdir /liboqs && \
cd /liboqs && \
wget https://github.com/open-quantum-safe/liboqs/archive/refs/tags/$LIBOQS_VERSION.zip && \
unzip $LIBOQS_VERSION.zip && \
cd liboqs-$LIBOQS_VERSION && \
mkdir build && cd build && \
cmake -GNinja -DOQS_USE_OPENSSL=ON -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=/usr \
-DCMAKE_BUILD_TYPE=Release -DOQS_BUILD_ONLY_LIB=ON .. && \
ninja && ninja install && \
cd / && rm -R /liboqs && \
# download and build strongSwan IKEv2 daemon
mkdir /strongswan-build && \
cd /strongswan-build && \
wget https://download.strongswan.org/strongswan-$VERSION.tar.bz2 && \
tar xfj strongswan-$VERSION.tar.bz2 && \
cd strongswan-$VERSION && \
./configure --prefix=/usr --sysconfdir=/etc --disable-ikev1       \
--enable-frodo --enable-oqs --enable-silent-rules  && \
make all && make install && \
cd / && rm -R strongswan-build && \
ln -s /usr/libexec/ipsec/charon charon && \
\
# clean up
apt-get -y remove $DEV_PACKAGES && \
apt-get -y autoremove && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*
