#!/bin/sh
# RSYNCSERVER=install.jumpscale.org
# if [ -n $1 ]; then
#     RSYNCSERVER=$1
# fi

mkdir -p /opt/jsbox
rsync -av -v install.jumpscale.org::download/test/jsbox/ /opt/jsbox/  --delete-after --modify-window=60 --compress --stats  --progress
rsync -av -v install.jumpscale.org::download/test/jsbox_data/ /opt/jsbox_data/  --delete-after --modify-window=60 --compress --stats  --progress
source /opt/jsbox/activate
jpackage install -n redis
rm -rf /opt/jsbox/cfg #resolve a bug

echo "JSBOX has been installed to activate it run 'source /opt/jsbox/activate'"
