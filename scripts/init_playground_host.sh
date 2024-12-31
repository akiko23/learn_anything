#!/bin/bash

mkdir -p /etc/learn_anything/qemu_disk_images
cp ./images/debian12-2_python_base.qcow2 /etc/learn_anything/qemu_disk_images
cp -r ./scripts/ /etc/learn_anything/
chmod ug+x -R /etc/learn_anything/scripts/
