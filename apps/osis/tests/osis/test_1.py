import unittest
import re, time
from OpenWizzy import o
from pylabs.Shell import ipshellDebug,ipshell
import random
client = o.core.osis.getClient()

def randomMAC():
        mac = [ 0x00, 0x16, 0x3e,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))



class OSISSearchTests(unittest.TestCase):

    def setUp(self):
        print 'setup'
        self.client = o.core.osis.getClient()
        self.prefix = time.time()
        #We make some basic entries to search on 
        numbers = range(10)
        self.created = []
        for i in numbers:
            macaddr = randomMAC()
            netaddr = {macaddr:['127.0.0.1', '127.0.0.2']}
            machineguid = o.tools.hash.md5_string(str(netaddr.keys()))
            obj=o.core.grid.zobjects.getZNodeObject(name="%s_%s" %
                    (self.prefix,i), netaddr = netaddr, machineguid =
                    machineguid)
            key,new,changed=client.set("system","znode",obj)
            self.created.append(key)

    def tearDown(self):
        #cleanup of al created entries
        print 'delete'
        for i in self.created:
            client.delete("system", "znode", i)

    def test_set_search_all(self):
        result = self.client.search("system", "znode", {})
        print result



class OSISTests(unittest.TestCase):


    def randomMAC(self):
        mac = [ 0x00, 0x16, 0x3e,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def setUp(self):
        self.client = o.core.osis.getClient()
        self.prefix = time.time()

    def test_set(self):
        #We first set some elements and verify the reponse
        macaddr = self.randomMAC()
        netaddr = {macaddr:['127.0.0.1', '127.0.0.2']}
        machineguid = o.tools.hash.md5_string(str(netaddr.keys()))
        obj=o.core.grid.zobjects.getZNodeObject(name="%s_1" % self.prefix,
                netaddr = netaddr, machineguid = machineguid)
        key,new,changed=client.set("system","znode",obj)
        testresult = new and not changed and self.verify_id(key)
        self.assertEqual(testresult, True)

    def test_set_and_get(self):
        #Set a object and get it back, check the content.
        macaddr = self.randomMAC()
        netaddr = {macaddr:['127.0.0.1', '127.0.0.2']}
        machineguid = o.tools.hash.md5_string(str(netaddr.keys()))
        obj=o.core.grid.zobjects.getZNodeObject(name="%s_1" % self.prefix,
                netaddr = netaddr, machineguid = machineguid)
        key,new,changed=client.set("system","znode",obj)
        obj=client.get("system","znode",key)
        self.assertEqual(obj['name'], "%s_1" % self.prefix)

    def test_set_and_self(self):
        numbers = range(10)
        items = client.list("system", "znode")
        startnr = len(items)
        for i in numbers:
            macaddr = self.randomMAC()
            netaddr = {macaddr:['127.0.0.1', '127.0.0.2']}
            machineguid = o.tools.hash.md5_string(str(netaddr.keys()))
            obj=o.core.grid.zobjects.getZNodeObject(name="%s_%s" %
                    (self.prefix,i), netaddr = netaddr, machineguid =
                    machineguid)
            key,new,changed=client.set("system","znode",obj)
        items = client.list("system", "znode")
        self.assertEqual(len(items), startnr + 10)

    def test_set_and_delete(self):
        macaddr = self.randomMAC()
        netaddr = {macaddr:['127.0.0.1', '127.0.0.2']}
        machineguid = o.tools.hash.md5_string(str(netaddr.keys()))
        obj=o.core.grid.zobjects.getZNodeObject(name="%s_1" % self.prefix,
                netaddr=netaddr, machineguid=machineguid)
        key,new,changed=client.set("system","znode",obj)
        obj=client.get("system","znode",key)
        client.delete("system", "znode", key)
        items  = client.list("system", "znode")
        if key in items:
            deleted = False
        else:
            deleted = True
        self.assertEqual(deleted, True)


    def verify_id(self, id):
        """
        This function verifies a id, e.g checks if its in the correct format
        Id should be clusterid_objectid
        Clusterid and objectid are both integers
        """
        regex = '^\d+[_]\d+$'
        if re.search(regex, id):
            return True
        else:
            return False



if __name__ == '__main__':
    unittest.main()
