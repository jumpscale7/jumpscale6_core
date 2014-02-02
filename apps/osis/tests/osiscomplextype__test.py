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
priority=3

import JumpScale.grid.osis


class TEST():

    def setUp(self):
        self.client = j.core.osis.getClient(user='root')
        self.osisclient =j.core.osis.getClientForCategory(self.client, 'test_complextype', 'project')
   
    def test_set(self):
        # We first set some elements and verify the reponse
        obj = self.osisclient.new()
        obj.descr="test descr"
        for i in range (5):
            task=obj.new_task()
            task.name="a task %s"%i
            task.priority=i
        
        assert obj.getContentKey()=='4e2e3a33a5887669070a2dcc6fc4888a'
        
        ckeyOriginal=obj.getContentKey()

        key,new,changed=self.osisclient.set(obj)
        key2,new,changed=self.osisclient.set(obj)

        print "2x save should have same key"
        assert key==key2

        print "check 2nd save new & changed are not new or changed"
        assert new==False
        assert changed==False

        print "test content key does not get modified when set"
        assert ckeyOriginal==obj.getContentKey()

        print "retrieve obj from db"
        obj2=self.osisclient.get(key)
        print "test content key needs to remain same after fetching object"

        assert ckeyOriginal==obj2.getContentKey()

        obj.description="a descr"
        print "obj needs to be different"
        assert ckeyOriginal<>obj.getContentKey()
        key3,new,changed=self.osisclient.set(obj)
        print "check 3nd save new & changed are False,True for modified obj"
        assert new==False
        assert changed==True
        print "key should be same"
        assert key==key3

        obj3=self.osisclient.get(key3)
        print "guid should be same even after content change"
        assert obj3.guid==key

    def test_find(self):
        # We first set some elements and verify the reponse
        for x in range(2):  #this should not make new elements
            for t in range(5):
                obj = self.osisclient.new()
                obj.name="name%s"%t
                obj.descr="test descr"
                for i in range (5):
                    task=obj.new_task()
                    task.name="a task %s %s"%(t,i)
                    task.priority=i
                key,new,changed=self.osisclient.set(obj)

        q='{"query":{"bool":{"must":[{"text":{"json.name":"name1"}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"facets":{}}'
        items=self.osisclient.search(q)

        assert items["total"]==1 #there should be only 1 (even the fact we stored in 2x, this because of overrule on setguid method)

        items=self.osisclient.simpleSearch(params={"name":"name3"})

        assert len(items)==1 #there should be only 1 (even the fact we stored in 2x, this because of overrule on setguid method)


    def tearDown(self):
        pass
