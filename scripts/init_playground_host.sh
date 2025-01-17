#!/bin/bash

VM_IMAGES_BASE_PATH=/etc/learn_anything/qemu_disk_images
VM_IMAGES_ARCHIVE_LINK=https://drive.google.com/uc?id=1h8X-hCrKKBgAKEvuPgjLcOW1-gpwo17R

poetry run gdown $VM_IMAGES_ARCHIVE_LINK

mkdir -p $VM_IMAGES_BASE_PATH

tar -xvzf vm_images.tar.gz -C $VM_IMAGES_BASE_PATH
mv $VM_IMAGES_BASE_PATH/images/* $VM_IMAGES_BASE_PATH && rm -r $VM_IMAGES_BASE_PATH/images

cp -r ./scripts/ /etc/learn_anything/
chmod ug+x -R /etc/learn_anything/scripts/
