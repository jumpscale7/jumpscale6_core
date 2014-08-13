#!/bin/bash
cleanup () {
        if [ "$KEEPVM" != "true" ]; then
    	    sudo lxc-destroy -f -n "$BUILD_TAG"
        fi
}

gettime () {
    uglytime=$(stat "/var/lib/lxc/$1/config" | grep Change | cut -d ' ' -f2,3,4)
    date -d "$uglytime" +'%s' 
}

#remove old machines
machines=$(sudo lxc-ls jenkins-JumpScale)
for machine in $machines; do
    time=$(gettime $machine)
    if [ $time -lt $(($(date +'%s') - 3600*24)) ]; then
        sudo lxc-destroy -fn $machine &
    fi
done


sudo lxc-clone -o saucy -n "$BUILD_TAG" -s -B overlayfs
sudo lxc-start -d -n "$BUILD_TAG"
sudo lxc-wait -n "$BUILD_TAG" -s RUNNING
vmip="-"
cnt=0
while [ "$vmip" = "-" -a $cnt -lt 20 ]; do
	vmip=$(sudo lxc-ls --fancy --fancy-format name,ipv4 | grep "$BUILD_TAG" | awk '{print $2}')
	sleep 1
	cnt=$(($cnt +1 ))
done
if [ "$vmip" = "-" ]; then
    echo "Failed to get the ip"
    cleanup
	exit 1
fi
ssh root@$vmip mkdir -p /opt/code/github/jumpscale
for repo in grid portal core lib; do
    rsync -a "$WORKSPACE/" root@$vmip:/opt/code/github/jumpscale/
done
set +e
ssh root@$vmip << EOF
chown -R root:root /opt/code/github/jumpscale/
set -e
set -x
apt-get update
apt-get install python-git ssh libmhash2 python2.7 python-apt openssl ca-certificates python-pip ipython python-requests -y
cd /opt/code/github/jumpscale/jumpscale_core/
pip install .

mkdir -p /opt/jumpscale/cfg/hrd/
mkdir -p /opt/jumpscale/cfg/jsconfig

echo 'elasticsearch.cluster.name=$BUILD_TAG' > /opt/jumpscale/cfg/hrd/elasticsearch.hrd
echo '
grid.id=13
grid.node.id=1
grid.watchdog.secret=rooter
grid.master.superadminpasswd=rooter
system_superadmin_login=root
' > /opt/jumpscale/cfg/hrd/grid.hrd

echo '[jumpscale]
passwd = 
login = 
[incubaid]
passwd = 
login = ' > /opt/jumpscale/cfg/jsconfig/github.cfg

jpackage mdupdate
jpackage install -n base

jpackage install -n mailclient -r --data="\
mail.relay.addr=smtp.mandrillapp.com #\
mail.relay.port=587 #\
mail.relay.ssl=1 #\
mail.relay.username=support@mothersip1.com #\
mail.relay.passwd=RVPrWxhyFF7I1s0GGtxt9Q"

#install mongodb (if local install)
jpackage install -n mongodb -i main -r --data="\
mongodb.host=127.0.0.1 #\
mongodb.port=27017 #\
mongodb.name=main"

#install mongodb client
jpackage install -n mongodb_client -i main -r --data="\
mongodb.client.addr=localhost #\
mongodb.client.port=27017 #\
mongodb.client.login= #\
mongodb.client.passwd="

#install influxdb (if local install)
jpackage install -n influxdb -i main -r --data="influxdb.seedservers:"

#install influxdb client
jpackage install -n influxdb_client -i main -r --data="\
influxdb.client.addr=localhost #\
influxdb.client.port=8086 #\
influxdb.client.login=root #\
influxdb.client.passwd=root"

#install osis (if local install)
jpackage install -n osis -i main -r --data="\
osis.key= #\
osis.connection=mongodb:main influxdb:main #\
osis.superadmin.passwd=rooter"

#install osis client (if remote install, then no mongodb client nor server required)
jpackage install -n osis_client -i main -r --data="\
osis.client.addr=localhost #\
osis.client.port=5544 #\
osis.client.login=root #\
osis.client.passwd=rooter"

#create admin user for e.g. portal
jsuser set -d admin:admin:admin:fakeemail.com:incubaid


#install webdis
jpackage install -n webdis -i main

#install webdis_client
jpackage install -n webdis_client -i main --data="\
addr=127.0.0.1 #\
port=7779"

#agentcontroller
jpackage install -n agentcontroller -i main --data="\
osis.connection=main #\
webdis.connection=main"

#agentcontrolller client
jpackage install -n agentcontroller_client -i main --data="\
agentcontroller.client.addr=127.0.0.1 #\
agentcontroller.client.port=4444"

#processmanager
jpackage install -n processmanager -i main --data="\
agentcontroller.connection=main #\
webdis.connection=main"

#workers
jpackage install -n workers

pip install nose

nosetests -v --with-xunit --xunit-file=/opt/tests.xml  /opt/code/jumpscale/${BRANCH}__jumpscale_grid/apps/osis/tests/*  /opt/code/jumpscale/${BRANCH}__jumpscale_grid/apps/agentcontroller/tests/* /opt/code/jumpscale/${BRANCH}__jumpscale_grid/apps/processmanager/tests/* /opt/code/jumpscale/${BRANCH}__jumpscale_grid/test/*

EOF

#/opt/code/jumpscale/jumpscale_grid/apps/gridportal/tests/*
exitcode=$?

echo "Installed ended with status $exitcode"

sudo cp "/var/lib/lxc/${BUILD_TAG}/delta0/opt/tests.xml" $WORKSPACE/tests.xml

if [ $exitcode -eq 0 ]; then
	cleanup
	exit 0
fi
echo "Failure happend leaving container behind as evidence"
