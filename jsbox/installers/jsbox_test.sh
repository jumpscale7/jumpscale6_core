#!/bin/sh
rsync -av -v 95.85.60.252::download/test/jsbox/ /opt/jsbox/  --delete-after --modify-window=60 --compress --stats  --progress
rsync -av -v 95.85.60.252::download/unstable/jsbox_data/ /opt/jsbox_data/  --delete-after --modify-window=60 --compress --stats  --progress
sh /opt/jsbox/tools/init.sh
export JSBASE=/opt/jsbox
jpackage install -n redis

