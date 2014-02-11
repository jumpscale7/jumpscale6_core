from JumpScale import j

import unittest

import JumpScale.grid.geventws

# j.application.start("test")

descr = """
test jumpscripts in processmanager
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "processmanager.jumpscripts"
enable=True
priority=5

class TEST():

    def setUp(self):
        self.client= j.servers.geventws.getClient("127.0.0.1", 4445, org="myorg", user=j.application.config.get('system.superadmin.login'), \
            passwd=j.application.config.get('grid.master.superadminpasswd'),category="jumpscripts")

    def test_loadJumpscripts(self):
        self.client.loadJumpscripts()

    def test_getJumpscript(self):
        result=self.client.getJumpscript(organization="jumpscale",name="disk_monitoring")        

        #how can we check that there needs to be an error @todo
        # error=False
        # try:
        #     result=self.client.getJumpscript(organization="jumpscale",name="startcheckprocessesssssss")
        # except:
        #     error=True
        # if error==False:
        #     raise RuntimeError("did not see error")


    def test_listJumpscripts(self):
        result=self.client.listJumpScripts()

        if len(result)<4:
            raise RuntimeError("needs to have more than 4 scripts")

        result=self.client.listJumpScripts(cat="startupmanager.check")
        if len(result)>1:
            raise RuntimeError("only 1 answer on this cat")

        result=self.client.listJumpScripts(organization="jumpscale")
        if len(result)<4:
            raise RuntimeError("need more than 4")
