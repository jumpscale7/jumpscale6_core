#!/usr/bin/env python
__author__ = 'delandtj'
from JumpScale import j
from JumpScale.baselib import cmdutils

import sys,time

j.application.start("jsnet")

import VXNet.netclasses as netcl

vxbackend = 'vxbackend'
def verify_memberships():
    with open ('/proc/sys/net/ipv4/igmp_max_memberships','r+') as f:
        val = f.read()
        if int(val.split()[0]) < 400:
            print("WARNING: set net.ipv4.igmp_max_memberships = 400 in /etc/sysctl.conf")
            f.write('400')
    with open ('/proc/sys/net/ipv4/igmp_max_msf','r+') as f:
        val = f.read()
        if int(val.split()[0]) < 400:
            print("WARNING: set net.ipv4.igmp_max_memberships = 400 in /etc/sysctl.conf")
            f.write('400')




if __name__ == "__main__":
    print('Getting Config')
    a = netcl.NetLayout()
    a.load()
    layout = a.nicdetail
    spaces = []
    for i in layout:
        if not layout[i]['params'].has_key('type'): continue
        if layout[i]['params']['type'] == 'bridge' and 'space_' in i:
            oid = netcl.NetID(i[6:])
            if not layout.has_key('vx-%s' % oid.tostring()):
                print('vx-%s not existing, creating' % oid.tostring())
                vxlan = netcl.VXlan(oid, vxbackend)
                vxlan.create()
                bridge = netcl.VXBridge(oid)
                print('connecting vx-%s to space_%s' %(oid.tostring()))
                bridge.connect(vxlan.name)

j.application.stop()
