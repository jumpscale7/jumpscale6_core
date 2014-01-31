import unittest
import re
import time
from JumpScale import j
import json
import random

descr = """
basic functioning of osis (test set) for complex types
"""

organization = "jumpscale"
author = "incubaid"
license = "bsd"
version = "1.0"
category = "osis.complextype.testset"
enable=True
priority=2

import JumpScale.grid.osis


class TEST():

    def setUp(self):
        self.client = j.core.osis.getClient(user='root')
        self.projclient =j.core.osis.getClientForCategory(self.client, 'test_complextype', 'project')
        

    def test_set(self):
        # We first set some elements and verify the reponse
        obj = self.projclient.new()
        obj.descr="test descr"
        obj.descr="test descr"
        for i in range (5):
            task=obj.new_task()
            task.name="a task %s"%i
            task.priority=i
        
        key, new, changed = self.projclient.set(obj)

        from IPython import embed
        print "DEBUG NOW ooo"
        embed()
        

        testresult = self.verify_id(key) and new and changed
        assert testresult==True

    # def test_set_and_get(self):
    #     # Set a object and get it back, check the content.
    #     obj = self.nodeclient.new()
    #     obj.name = "%s_1" % self.prefix
    #     obj.netaddr = {self.randomMAC(): ['127.0.0.1', '127.0.0.2']}
    #     obj.machineguid = j.tools.hash.md5_string(str(obj.netaddr.keys()))
    #     key, new, changed = self.nodeclient.set(obj)
    #     obj = json.loads(self.client.get("system", "fake4test", key))
    #     assert obj['name']== "%s_1" % self.prefix

    # def test_set_and_self(self):
    #     numbers = range(10)
    #     items = self.client.list("system", "fake4test")
    #     startnr = len(items)
    #     for i in numbers:
    #         obj = self.nodeclient.new()
    #         obj.name = "%s_%s" % (self.prefix, i)
    #         obj.netaddr = {self.randomMAC(): ['127.0.0.1', '127.0.0.2']}
    #         obj.machineguid = j.tools.hash.md5_string(str(obj.netaddr.keys()))
    #         key, new, changed = self.nodeclient.set(obj)
    #     items = self.client.list("system", "fake4test")
    #     assert len(items)== startnr + 10

    # def test_set_and_delete(self):
    #     obj = self.nodeclient.new()
    #     obj.name = "%s_1" % self.prefix
    #     obj.netaddr = {self.randomMAC(): ['127.0.0.1', '127.0.0.2']}
    #     obj.machineguid = j.tools.hash.md5_string(str(obj.netaddr.keys()))
    #     key, new, changed = self.nodeclient.set(obj)
    #     obj = self.client.get("system", "fake4test", key)
    #     self.client.delete("system", "fake4test", key)
    #     items = self.client.list("system", "fake4test")
    #     if key in items:
    #         deleted = False
    #     else:
    #         deleted = True
    #     assert deleted==True

    # def test_find(self):
    #     pass

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

    def tearDown(self):
        pass
