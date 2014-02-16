#!/bin/bash
cleanup () {
        if [ "$KEEPVM" != "true" ]; then
    	    sudo lxc-destroy -f -n "$BUILD_TAG"
        fi
}

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
rsync -a "$WORKSPACE/" root@$vmip:/opt/code/
set +e
ssh root@$vmip "
chown -R root:root /opt/code/jumpscale/jumpscale_core
set -e
apt-get update
apt-get install mercurial ssh python2.7 python-apt openssl ca-certificates python-pip ipython python-requests -y
cd /opt/code/jumpscale/jumpscale_core/
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
jpackage install -n core

jpackage install -n grid_master
jpackage install -n grid_node
jpackage install -n logger
jpackage install -n grid_portal
jpackage install -n processmanager
jpackage install -n graphite
jpackage install -n agentcontroller
jpackage install -n agent

echo '[main]
appdir = /opt/jumpscale/apps/portalbase

filesroot = $vardir/portal/files

actors = *
webserverport = 81

#leave 0 if disabled (this is like secret which gives access to all)
secret=1234

#groups which get access to admin features of portal
admingroups=admin,gridadmin,superadmin

pubipaddr=127.0.0.1
' > /opt/jumpscale/apps/gridportal/cfg/portal.cfg

jsprocess start

pip install nose

nosetests --with-xunit --xunit-file=/opt/tests.xml  /opt/code/jumpscale/jumpscale_grid/apps/osis/tests/*  /opt/code/jumpscale/jumpscale_grid/apps/agentcontroller/tests/* /opt/code/jumpscale/jumpscale_grid/apps/processmanager/tests/*

"
#/opt/code/jumpscale/jumpscale_grid/apps/gridportal/tests/*
exitcode=$?

sudo cp "/var/lib/lxc/${BUILD_TAG}/delta0/opt/tests.xml" $WORKSPACE/tests.xml

if [ $exitcode -eq 0 ]; then
	cleanup
	exit 0
fi
echo "Failure happend leaving container behind as evidence"
sudo lxc-stop -n "$BUILD_TAG"
cleanup
