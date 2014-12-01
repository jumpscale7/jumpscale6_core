from JumpScale import j

import unittest

import JumpScale.grid.geventws

# j.application.start("test")

descr = """
test startup manager, to list/start/stop processes
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "processmanager.startupmanager"
enable=True
priority=5

class TEST():

    def setUp(self):
        self.client= j.servers.geventws.getClient("127.0.0.1", 4446, org="myorg", user=j.application.config.get('system.superadmin.login'), \
    passwd=j.application.config.get('grid.master.superadminpasswd'),category="startupmanager")

    def test_getdomains(self):
        self.domains=self.client.getDomains()

    def test_startAll(self):
        self.client.startAll()

    def test_getStatus4JPackage(self):
        print self.client.getStatus4JPackage("jumpscale","osis")

    def test_getStatus(self):
        print self.client.getStatus("jumpscale","osis")

    def test_listProcesses(self):
        llist=self.client.listProcesses()
        if len(llist)<1:
            raise RuntimeError("need to be at least 1")
        
    def test_getProcessesActive(self):
        llist=self.client.getProcessesActive()
        if len(llist)<1:
            raise RuntimeError("need to be at least 1")

    #@todo finish tests and make better, need to interact with startup manager locally and manually remove & set some files


