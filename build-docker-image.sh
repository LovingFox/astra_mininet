#!/bin/sh

REPO="https://dl.astralinux.ru/astra/stable/orel/repository"

set -e

IMAGE_NAME="astra_linux_ce"
IMAGE_VER="2.12"

IMAGE="$IMAGE_NAME-frr:$IMAGE_VER"
ROOTFS_IMAGE="$IMAGE_NAME-rootfs:$IMAGE_VER"
CODENAME="orel"

echo $IMAGE
echo $ROOTFS_IMAGE
echo $CODENAME

sleep 5

for required_pkg in docker.io debootstrap ; do
    dpkg -s $required_pkg 2>&1 >/dev/null || \
        (printf 'Please install %s package\n' $required_pkg;\
        exit 1)
done

# Check docker can be run without sudo
docker version 2>&1 >/dev/null ||\
    (printf 'Please run with sudo or add your account to `docker` group\n';\
    exit 1)

TMPDIR=`mktemp -d`
cd $TMPDIR

cleanup() {
    cd $HOME
    # debootstrap leaves mounted /proc and /sys folders in chroot
    # when terminated by Ctrl-C
    sudo umount $TMPDIR/proc $TMPDIR/sys 2>&1 >/dev/null || true
    # Delete temporary data at exit
    sudo rm -rf $TMPDIR
}
trap cleanup EXIT

sudo -E debootstrap --no-check-gpg --variant=minbase \
    --include=apt-transport-https,ca-certificates,lsb-release,iproute2,net-tools,curl,procps,iputils-ping \
    --components=main,contrib,non-free "$CODENAME" ./chroot "$REPO"

sudo chroot $(pwd)/chroot bash <<EOF
curl -s https://deb.frrouting.org/frr/keys.asc | apt-key add -
echo deb https://deb.frrouting.org/frr stretch frr-stable | tee -a /etc/apt/sources.list.d/frr.list
apt-get update && apt-get install -y frr frr-pythontools
sed -i 's/ripd=no/ripd=yes/' /etc/frr/daemons
sed -i 's/ospfd=no/ospfd=yes/' /etc/frr/daemons
for DIR in /usr/share/man /var/cache/apt /var/lib/apt/lists /usr/share/locale /var/log /usr/share/info
do rm -rf \$DIR/*; done
find /usr/share/doc -mindepth 2 -not -name copyright -not -type d -delete
find /usr/share/doc -mindepth 1 -type d -empty -delete
EOF

echo "deb $REPO $CODENAME contrib main non-free" | sudo tee ./chroot/etc/apt/sources.list

docker rmi "$ROOTFS_IMAGE" >/dev/null 2>&1 || true

sudo tar -C chroot -c . | docker import - "$ROOTFS_IMAGE"

docker build --network=host --no-cache=true -t "$IMAGE" - <<EOF
FROM $ROOTFS_IMAGE
ENV TERM xterm-256color \
    DEBIAN_FRONTEND noninteractive
CMD /usr/lib/frr/frrinit.sh start && bash
EOF

printf 'Docker image `%s` has been generated\n' "$IMAGE"
exit 0

