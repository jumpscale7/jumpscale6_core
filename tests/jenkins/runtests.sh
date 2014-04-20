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
machines=$(sudo lxc-ls jenkins)
for machine in machines; do
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
ssh root@$vmip mkdir -p /opt/code/jumpscale
for repo in grid portal core lib; do
    rsync -a "$WORKSPACE/jumpscale/jumpscale_$repo/" root@$vmip:/opt/code/jumpscale/${BRANCH}__jumpscale_${repo}
done
set +e
ssh root@$vmip "
chown -R root:root /opt/code/jumpscale/${BRANCH}__jumpscale_core
set -e
set -x
apt-get update
apt-get install mercurial ssh python2.7 python-apt openssl ca-certificates python-pip ipython python-requests -y
cd /opt/code/jumpscale/${BRANCH}__jumpscale_core/
pip install .

mkdir -p /opt/jumpscale/cfg/hrd/
mkdir -p /opt/jumpscale/cfg/jsconfig

echo 'elasticsearch.cluster.name=mycluster' > /opt/jumpscale/cfg/hrd/elasticsearch.hrd
echo 'broker.id=1
broker.domain=mydomain' > /opt/jumpscale/cfg/hrd/broker.hrd
echo '
grid.id=1
grid.node.id=1
grid.useavahi=1
grid.ismaster=True
grid.master=
grid.master.ip=localhost
grid.node.roles=node,computenode,kvm
grid.master.superadminpasswd=6bde6ce08268a6d58ba96f27402bd7d4
' > /opt/jumpscale/cfg/hrd/grid.hrd

echo '
redis.port.redisc=7767
redis.port.redisp=7768
redis.port.redisac=7769
redis.port.redism=7766
redis.ac.enable=1
' > /opt/jumpscale/cfg/hrd/redis.hrd

echo '
gridmaster.useavahi=1
gridmaster.grid.id=1' > /opt/jumpscale/cfg/hrd/grid_master.hrd

echo 'osis.key=mykey' > /opt/jumpscale/cfg/hrd/osis.hrd

echo '[jumpscale]
passwd = qp55pq
login = qp5
[incubaid]
passwd = qp55pq
login = qp5' > /opt/jumpscale/cfg/jsconfig/bitbucket.cfg


jpackage mdupdate
jpackage install -n base
jpackage install -n grid_master_singlenode

echo '[main]
appdir = /opt/jumpscale/apps/portalbase
filesroot = $vardir/portal/files
actors = *
webserverport = 81
secret=1234
admingroups=admin,gridadmin,superadmin
pubipaddr=127.0.0.1
' > /opt/jumpscale/apps/gridportal/cfg/portal.cfg

jsprocess start
jpackage install -n processmanager

pip install nose

nosetests -v --with-xunit --xunit-file=/opt/tests.xml  /opt/code/jumpscale/${BRANCH}__jumpscale_grid/apps/osis/tests/*  /opt/code/jumpscale/${BRANCH}__jumpscale_grid/apps/agentcontroller/tests/* /opt/code/jumpscale/${BRANCH}__jumpscale_grid/apps/processmanager/tests/* /opt/code/jumpscale/${BRANCH}__jumpscale_grid/test/*

"
#/opt/code/jumpscale/jumpscale_grid/apps/gridportal/tests/*
exitcode=$?

sudo cp "/var/lib/lxc/${BUILD_TAG}/delta0/opt/tests.xml" $WORKSPACE/tests.xml

if [ $exitcode -eq 0 ]; then
	cleanup
	exit 0
fi
echo "Failure happend leaving container behind as evidence"
