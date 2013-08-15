#-*- coding: utf-8 -*-

import unittest
from OpenWizzy import o
import OpenWizzy.baselib.serializers

class test_SerializerHRD(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_loadsdumps(self):
        test_dumps1 = {'name':'machinename'}
        dumped = o.db.serializers.hrd.dumps(test_dumps1)   
        self.assertEquals(dumped, 'name = machinename\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps1)

        test_dumps2 = {'name':'machinename',
                      'disks':[{'diskname': 'disk1', 'size':256}]}
        dumped = o.db.serializers.hrd.dumps(test_dumps2)
        self.assertEquals(dumped, 'disks.[0].diskname = disk1\ndisks.[0].size. = 256\nname = machinename\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps2)

        test_dumps3 = {'name':'machinename',
                      'disks':[{'diskname': 'disk1', 'size':256}, {'diskname': 'disk2', 'size':999}]}
        dumped = o.db.serializers.hrd.dumps(test_dumps3)   
        self.assertEquals(dumped, 'disks.[0].diskname = disk1\ndisks.[0].size. = 256\ndisks.[1].diskname = disk2\ndisks.[1].size. = 999\nname = machinename\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps3)

        test_dumps4 = {'name':'machinename',
                      'disks':[{'diskname': 'disk1', 'size':256}, {'diskname': 'disk2', 'size':[1,3,4]}]}
        dumped = o.db.serializers.hrd.dumps(test_dumps4)   
        self.assertEquals(dumped, 'disks.[0].diskname = disk1\ndisks.[0].size. = 256\ndisks.[1].diskname = disk2\ndisks.[1].size.[0]. = 1\ndisks.[1].size.[1]. = 3\ndisks.[1].size.[2]. = 4\nname = machinename\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps4)

        test_dumps5 = {'name':'machinename',
                      'disks':[None, {'diskname': 'disk2', 'size':[1,3,4]}]}
        dumped = o.db.serializers.hrd.dumps(test_dumps5)   
        self.assertEquals(dumped, 'disks.[0]. = None\ndisks.[1].diskname = disk2\ndisks.[1].size.[0]. = 1\ndisks.[1].size.[1]. = 3\ndisks.[1].size.[2]. = 4\nname = machinename\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps5)

        test_dumps6 = {'name':'machinename',
                      'disks':[{}, {'diskname': 'disk2', 'size':[1,3,4]}]}
        dumped = o.db.serializers.hrd.dumps(test_dumps6)   
        self.assertEquals(dumped, 'disks.[0]. = {}\ndisks.[1].diskname = disk2\ndisks.[1].size.[0]. = 1\ndisks.[1].size.[1]. = 3\ndisks.[1].size.[2]. = 4\nname = machinename\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps6)

        test_dumps7 = {'name':'machinename',
                      'disks':[{'diskname': 'disk1', 'size':256}, {'diskname': 'disk2', 'size':[]}]}
        dumped = o.db.serializers.hrd.dumps(test_dumps7)   
        self.assertEquals(dumped, 'disks.[0].diskname = disk1\ndisks.[0].size. = 256\ndisks.[1].diskname = disk2\ndisks.[1].size. = []\nname = machinename\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps7)

        test_dumps8 = 'test'
        dumped = o.db.serializers.hrd.dumps(test_dumps8)   
        self.assertEquals(dumped, 'test')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps8)

        test_dumps9 = [1, 2, 3]
        dumped = o.db.serializers.hrd.dumps(test_dumps9)   
        self.assertEquals(dumped, '[0]. = 1\n[1]. = 2\n[2]. = 3\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps9)

        test_dumps10 = [[1,2],[3,4]]
        dumped = o.db.serializers.hrd.dumps(test_dumps10)   
        self.assertEquals(dumped, '[0].[0]. = 1\n[0].[1]. = 2\n[1].[0]. = 3\n[1].[1]. = 4\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps10)

        test_dumps11 = {'name':{'fname': 'fname', 'lname':'lname'}}
        dumped = o.db.serializers.hrd.dumps(test_dumps11)   
        self.assertEquals(dumped, 'name.lname = lname\nname.fname = fname\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps11)

        test_dumps12 = {'size':'256'}
        dumped = o.db.serializers.hrd.dumps(test_dumps12)   
        self.assertEquals(dumped, 'size = 256\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps12)

        test_dumps13 = {'size':256}
        dumped = o.db.serializers.hrd.dumps(test_dumps13)   
        self.assertEquals(dumped, 'size. = 256\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps13)

        test_dumps14 = 256
        dumped = o.db.serializers.hrd.dumps(test_dumps14)   
        self.assertEquals(dumped, '256.')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps14)

        test_dumps15 = {'nam..e':'machinename'}
        dumped = o.db.serializers.hrd.dumps(test_dumps15)
        self.assertEquals(dumped, 'nam..e = machinename\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps15)

        test_dumps16 = {'na..me':'machinename',
                      'disks':[{'diskn..ame': 'disk1', 'size':256}, {'diskname': 'dis..k2', 'size':999}]}
        dumped = o.db.serializers.hrd.dumps(test_dumps16)   
        self.assertEquals(dumped, 'disks.[0].diskn..ame = disk1\ndisks.[0].size. = 256\ndisks.[1].diskname = dis..k2\ndisks.[1].size. = 999\nna..me = machinename\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps16)

        test_dumps17 = [{'name..is': 'name'}, 'anotheritem']
        dumped = o.db.serializers.hrd.dumps(test_dumps17)   
        self.assertEquals(dumped, '[0].name..is = name\n[1] = anotheritem\n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps17)

        test_dumps18 = 'name..is'
        dumped = o.db.serializers.hrd.dumps(test_dumps18)   
        self.assertEquals(dumped, 'name..is')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps18)

        test_dumps19 = u'name..is'
        dumped = o.db.serializers.hrd.dumps(test_dumps19)   
        self.assertEquals(dumped, 'name..is')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps19)

        test_dumps20 = {u'passwd': u'admin', 
                        u'emails': [u''], 
                        u'secret': u'mysecret', 
                        u'groups': [u'admin'], 
                        u'guid': u'96ec17c7-e8ea-431e-9014-65b70be65b67', 
                        u'id': u'admin'}
        dumped = o.db.serializers.hrd.dumps(test_dumps20)
        self.assertEquals(dumped, 'passwd = admin\nid = admin\nsecret = mysecret\ngroups.[0] = admin\nguid = 96ec17c7-e8ea-431e-9014-65b70be65b67\nemails.[0] = \n')
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps20)

        test_dumps21 = u'présenté'
        dumped = o.db.serializers.hrd.dumps(test_dumps21)
        loaded = o.db.serializers.hrd.loads(dumped)
        self.assertEquals(loaded, test_dumps21)
