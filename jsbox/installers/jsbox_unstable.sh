#!/bin/sh
RSYNCSERVER=95.85.60.252
if [ -n $1 ]; then
    RSYNCSERVER=$1
fi

rsync -av -v $RSYNCSERVER::download/unstable/jsbox/ /opt/jsbox/  --delete-after --modify-window=60 --compress --stats  --progress
rsync -av -v $RSYNCSERVER::download/unstable/jsbox_data/ /opt/jsbox_data/  --delete-after --modify-window=60 --compress --stats  --progress
source /opt/jsbox/activate

echo "JSBOX has been installed to activate it run 'source /opt/jsbox/active'"
