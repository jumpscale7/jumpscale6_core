import unittest
import re
import time
from JumpScale import j
import json
import random


import JumpScale.grid.osis

client = j.core.osis.getClient()


def randomMAC():
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))


class OSISSearchTests(unittest.TestCase):

    def setUp(self):
        print 'setup'
        self.nodeclient =j.core.osis.getClientForCategory(client, 'system', 'node')

        self.prefix = time.time()
        # We make some basic entries to search on
        numbers = range(10)
        self.created = []
        for i in numbers:
            obj = self.nodeclient.new()
            obj.name = "%s_%s" % (self.prefix, i)
            obj.netaddr = {randomMAC(): ['127.0.0.1', '127.0.0.2']}
            obj.machineguid = j.tools.hash.md5_string(str(obj.netaddr.keys()))
            key, new, changed = self.nodeclient.set(obj)
            self.created.append(key)

    def tearDown(self):
        # cleanup of al created entries
        print 'delete'
        for i in self.created:
            client.delete("system", "node", i)

    def test_set_search_all(self):
        result = client.search("system", "node", {})
        print result


class OSISTests(unittest.TestCase):

    def randomMAC(self):
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def setUp(self):
        self.nodeclient =j.core.osis.getClientForCategory(client, 'system', 'node')
        self.prefix = time.time()

    def test_set(self):
        # We first set some elements and verify the reponse
        obj = self.nodeclient.new()
        obj.name = "%s_1" % self.prefix
        obj.netaddr = {randomMAC(): ['127.0.0.1', '127.0.0.2']}
        obj.machineguid = j.tools.hash.md5_string(str(obj.netaddr.keys()))
        key, new, changed = self.nodeclient.set(obj)
        testresult = self.verify_id(key) and new and changed
        self.assertEqual(testresult, True)

    def test_set_and_get(self):
        # Set a object and get it back, check the content.
        obj = self.nodeclient.new()
        obj.name = "%s_1" % self.prefix
        obj.netaddr = {randomMAC(): ['127.0.0.1', '127.0.0.2']}
        obj.machineguid = j.tools.hash.md5_string(str(obj.netaddr.keys()))
        key, new, changed = self.nodeclient.set(obj)
        obj = json.loads(client.get("system", "node", key))
        self.assertEqual(obj['name'], "%s_1" % self.prefix)

    def test_set_and_self(self):
        numbers = range(10)
        items = client.list("system", "node")
        startnr = len(items)
        for i in numbers:
            obj = self.nodeclient.new()
            obj.name = "%s_%s" % (self.prefix, i)
            obj.netaddr = {randomMAC(): ['127.0.0.1', '127.0.0.2']}
            obj.machineguid = j.tools.hash.md5_string(str(obj.netaddr.keys()))
            key, new, changed = self.nodeclient.set(obj)
        items = client.list("system", "node")
        self.assertEqual(len(items), startnr + 10)

    def test_set_and_delete(self):
        obj = self.nodeclient.new()
        obj.name = "%s_1" % self.prefix
        obj.netaddr = {randomMAC(): ['127.0.0.1', '127.0.0.2']}
        obj.machineguid = j.tools.hash.md5_string(str(obj.netaddr.keys()))
        key, new, changed = self.nodeclient.set(obj)
        obj = client.get("system", "node", key)
        client.delete("system", "node", key)
        items = client.list("system", "node")
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
