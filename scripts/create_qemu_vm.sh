#!/bin/bash

if [[ $1 == "--help" ]]; then
  echo "Usage: ./qemu_start.sh [fwd_port] [path_to_drive_file]"
  exit 0
fi

if ! [[ $1 && $2 ]]; then
  echo "Provide the necessary arguments. Check --help"
  exit 1
fi


fwd_port=$1
path_to_drive_file=$2

# for persistence remove -snapshot=on
sudo qemu-system-x86_64 \
  -M microvm \
  -drive file=$path_to_drive_file,format=qcow2,if=virtio,snapshot=on \
  -machine pc \
  -boot c \
  -enable-kvm -netdev user,id=mynet0,hostfwd=tcp::$fwd_port-:22 \
  -device e1000,netdev=mynet0 \
  -cpu host -m 256
