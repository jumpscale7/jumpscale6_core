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

echo '[jumpscale]
passwd = 
login = 
[incubaid]
passwd = 
login = ' > /opt/jumpscale/cfg/jsconfig/github.cfg

echo '
grid.master.superadminpasswd=rooter
grid.id=666
' >> /opt/jumpscale/cfg/hrd/grid.hrd

jpackage mdupdate
jpackage install -n base

jpackage install -n mailclient -r --data="\
mail.relay.addr=smtp.mandrillapp.com #\
mail.relay.port=587 #\
mail.relay.ssl=1 #\
mail.relay.username=support@mothersip1.com #\
mail.relay.passwd=RVPrWxhyFF7I1s0GGtxt9Q"

jpackage install -n grid_master_singlenode

pip install nose

nosetests -v --with-xunit --xunit-file=/opt/tests.xml  /opt/code/github/jumpscale/jumpscale_core/apps/osis/tests/*  /opt/code/github/jumpscale/jumpscale_core/apps/agentcontroller/tests/* /opt/code/github/jumpscale/jumpscale_core/apps/processmanager/tests/* /opt/code/github/jumpscale/jumpscale_core/test/*

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
