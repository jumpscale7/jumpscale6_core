import unittest
import re
import time
from JumpScale import j

import JumpScale.grid.osis

class OSISPopulationTest(unittest.TestCase):

    def setUp(self):
        print 'setup'
        self.client = j.core.osis.getClient()

    def tearDown(self):
        pass

    def test_log(self):
        pass

    def test_stat(self):

        client=j.core.osis.getClientForCategory(self.client,"system","stat")
    
        for i in range(10):
            keys=["cpu.percent",\
                "process.nrconnections",\
                "memory.rss",\
                "memory.vms",\
                "contentswitches"]
            for key in keys:
                obj=client.new()
                obj.key="n%s.test.%s"%(i,key)
                obj.nid=i
                client.set(obj)

    def test_node(self):
        print 'node'
        client=j.core.osis.getClientForCategory(self.client,"system","node")        

        for i in range(80,90):
            obj=client.new()
            obj.gid=1
            obj.nid=i
            mac1='46:3a:26:39:67:%s'%i
            mac2='00:22:4d:9a:ee:%s'%i
            netaddr={mac1: ['lxcbr0', '10.0.3.%s'%i], mac2: ['eth1', '192.168.200.%s'%i]}
            obj.netaddr=netaddr
            obj.peer_log=j.base.idgenerator.generateRandomInt(80,90)
            obj.peer_stats=j.base.idgenerator.generateRandomInt(80,90)
            obj.peer_backup=j.base.idgenerator.generateRandomInt(80,90)
            obj.machineguid="00224d9aee%s"%i
            obj.ipaddr=['10.0.3.%s'%i, '192.168.200.%s'%i]
            obj.name="name%s"%i
            obj.description = "this is a description for node %s"%i
            obj.active=j.base.idgenerator.generateRandomInt(10,14)==11
            client.set(obj)
        
    def test_machine(self):
        print 'machine'
        client=j.core.osis.getClientForCategory(self.client,"system","machine")        

        for i in range(30,50):

            obj=client.new()            
            obj.gid=1
            obj.nid=j.base.idgenerator.generateRandomInt(1,10)
            mac1='46:3a:26:39:33:%s'%i
            mac2='00:22:4d:9a:33:%s'%i
            netaddr={mac1: ['eth0', '10.0.3.%s'%i], mac2: ['eth1', '192.168.200.%s'%i]}
            obj.netaddr=netaddr
            obj.ipaddr=['10.0.3.%s'%i, '192.168.200.%s'%i]
            r=j.base.idgenerator.generateRandomInt(0,5)
            states=["STARTED","STOPPED","RUNNING","FROZEN","CONFIGURED","DELETED"]
            obj.state=states[r]
            obj.mem=j.base.idgenerator.generateRandomInt(0,10)*100
            obj.cpucore=j.base.idgenerator.generateRandomInt(0,12)            
            obj.name="name%s"%i
            obj.description = "this is a description for machine %s"%i
            obj.otherid="m%s"%(i+5)
            obj.active=j.base.idgenerator.generateRandomInt(10,14)==11
            obj.type="KVM"
            client.set(obj)

    def test_process(self):
        print 'process'
        client=j.core.osis.getClientForCategory(self.client,"system","process")        

        for i in range(30,1000):

            obj=client.new()            
            obj.gid=1
            obj.nid=obj.nid=j.base.idgenerator.generateRandomInt(1,10)
            obj.active=j.base.idgenerator.generateRandomInt(10,14)==11
            if j.base.idgenerator.generateRandomInt(1,5)==2:
                obj.instance=2
            else:
                obj.instance=1
            obj.systempid=j.base.idgenerator.generateRandomInt(4450,20888)
            obj.epochstart=self.epochstart = j.base.time.getTimeEpoch()-10000+j.base.idgenerator.generateRandomInt(0,10000)
            obj.epochstop=obj.epochstart+j.base.idgenerator.generateRandomInt(1,600)
            r=j.base.idgenerator.generateRandomInt(0,2)
            domains=["jumpscale","incubaid","adomain"]
            obj.jpdomain=domains[r]
            obj.jpname="jpname%s"%i
            obj.name="process%s"%i
            client.set(obj)

    def test_disk(self):
        print 'disk'
        client=j.core.osis.getClientForCategory(self.client,"system","disk")        

        for i in range(20,70):
            obj=client.new()            
            obj.gid=1
            obj.nid=obj.nid=j.base.idgenerator.generateRandomInt(1,10)
            obj.active=j.base.idgenerator.generateRandomInt(10,14)==11
            if j.base.idgenerator.generateRandomInt(1,5)==2:
                obj.ssd=True
            else:
                obj.ssd=False
            self.model="amodel %s"%i

            r=j.base.idgenerator.generateRandomInt(0,2)
            paths=["/dev/sda","/dev/sdb","/dev/sdc"]
            obj.path=paths[r]+str(j.base.idgenerator.generateRandomInt(0,3))
            obj.size=j.base.idgenerator.generateRandomInt(100000,2000000)
            obj.free=int(float(obj.size)*((float(j.base.idgenerator.generateRandomInt(1,9))/10)))

            fss=["ext4","btrfs","ext3","ntfs"]
            obj.fs=fss[j.base.idgenerator.generateRandomInt(0,3)]
            obj.mounted=not j.base.idgenerator.generateRandomInt(1,5)==2
            obj.name="disk%s"%i
            obj.description = "this is a description for disk %s"%i            
            ttype=["BOOT","DATA","SWAP","TEMP"]
            obj.type=ttype[j.base.idgenerator.generateRandomInt(0,3)]
            obj.mountpoint="/mnt/data/%s"%i

            client.set(obj)

    def test_vdisk(self):
        print 'vdisk'
        client=j.core.osis.getClientForCategory(self.client,"system","vdisk")        

        for i in range(20,70):
            obj=client.new()            
            obj.gid=1
            obj.nid=obj.nid=j.base.idgenerator.generateRandomInt(1,10)
            obj.disk_id=j.base.idgenerator.generateRandomInt(1,50)
            obj.machine_id=j.base.idgenerator.generateRandomInt(1,20)
            obj.active=j.base.idgenerator.generateRandomInt(10,14)==11

            r=j.base.idgenerator.generateRandomInt(0,2)
            obj.path="/mnt/data/%s/an_image%s.qcow2"%(obj.disk_id,i)
            obj.size=j.base.idgenerator.generateRandomInt(100000,2000000)
            obj.free=int(float(obj.size)*((float(j.base.idgenerator.generateRandomInt(1,9))/10)))
            obj.sizeondisk=j.base.idgenerator.generateRandomInt(100000,2000000)
            fss=["ext4","btrfs","ext3","ntfs"]
            obj.fs=fss[j.base.idgenerator.generateRandomInt(0,3)]
            obj.order=1
            obj.name="vdisk%s"%i
            obj.description = "this is a description for vdisk %s"%i            
            ttype=["BOOT","DATA"]
            obj.role=ttype[j.base.idgenerator.generateRandomInt(0,1)]
            obj.type="QCOW2"
            obj.backup=not j.base.idgenerator.generateRandomInt(1,5)==2
            if obj.backup:
                self.backuptime=j.base.time.getTimeEpoch()-j.base.idgenerator.generateRandomInt(100,2000)
                self.backuploaction="/mnt/abackuplocation/%s"%i
            client.set(obj)



if __name__ == '__main__':
    unittest.main()
