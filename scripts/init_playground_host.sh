#!/bin/bash

VM_IMAGES_BASE_PATH=/etc/learn_anything/qemu_disk_images


mkdir -p $VM_IMAGES_BASE_PATH

tar -xvzf vm_images/vm_images.tar.gz -C $VM_IMAGES_BASE_PATH
mv $VM_IMAGES_BASE_PATH/images/* $VM_IMAGES_BASE_PATH && rm -r $VM_IMAGES_BASE_PATH/images

cp -r ./scripts/ /etc/learn_anything/
chmod ug+x -R /etc/learn_anything/scripts/
