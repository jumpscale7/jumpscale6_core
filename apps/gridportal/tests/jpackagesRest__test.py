from JumpScale import j

import JumpScale.portal

descr = """
test jpackages over rest to portal (appserver)
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "appserver.jpackages.rest,portal"
enable=True
priority=5

class TEST():

    def setUp(self):
        self.client= j.core.portal.getPortalClient("127.0.0.1", 9900, "1234")  #@need to read from config file for the secret
        self.actor = self.client.getActor("system", "packagemanager")
        

    def test_getJpackages(self):
        l1=self.actor.getJPackages(j.application.whoAmI.nid)
        print l1
        l2=self.actor.getJPackages(j.application.whoAmI.nid,"jumpscale")
        print l2

    def test_getJpackageInfo(self):
        jp=self.actor.getJPackageInfo(j.application.whoAmI.nid,"jumpscale","osis")
        print jp


    def test_getJpackageFilesInfo(self):
        info=self.actor.getJPackageFilesInfo(j.application.whoAmI.nid,"jumpscale","osis")
        # print info

    def test_action(self):
        info=self.actor.action(j.application.whoAmI.nid,domain="jumpscale",pname="osis",action="start")
        print info


        


    #@todo finish tests and make better

