#!/bin/sh
rsync -av -v 95.85.60.252::download/test/jsbox/ /opt/jsbox/  --delete-after --modify-window=60 --compress --stats  --progress
sh /opt/jsbox/tools/init.sh

