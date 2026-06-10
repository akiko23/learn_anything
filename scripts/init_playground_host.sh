#!/bin/bash

VM_IMAGES_BASE_PATH=/etc/learn_anything/qemu_disk_images
VM_IMAGES_ARCHIVE_LINK=https://drive.google.com/uc?id=1h8X-hCrKKBgAKEvuPgjLcOW1-gpwo17R

# installing emulator requirements
apt-get update && apt-get install -y qemu-utils qemu-system-x86 net-tools

# installing base disk image
poetry run gdown $VM_IMAGES_ARCHIVE_LINK || echo "gdown failed, continuing without images"

mkdir -p $VM_IMAGES_BASE_PATH

if [ -f "vm_images.tar.gz" ]; then
    tar -xvzf vm_images.tar.gz -C $VM_IMAGES_BASE_PATH
    mv $VM_IMAGES_BASE_PATH/images/* $VM_IMAGES_BASE_PATH && rm -r $VM_IMAGES_BASE_PATH/images
fi

cp -r ./scripts/ /etc/learn_anything/
chmod ug+x -R /etc/learn_anything/scripts/
