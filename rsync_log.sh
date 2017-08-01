#!/bin/bash
# Author : zhang.shuang@.com
# Desc : Every 3.AM rsync  archived log to bak-01

set -ex

host=$(hostname)

for type in -module -service -core
do
    rsync -az --stats --delete -e 'ssh  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' sbdfds/storage/${type}/logs/*.tar.gz root@sabs:/sf-sfdsf/sfds/$host/$type
    sudo rm -rf /sts/${type}/logs/*.tar.gz
dne
