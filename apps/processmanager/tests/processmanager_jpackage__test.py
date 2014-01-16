from JumpScale import j

import JumpScale.grid.geventws

# j.application.start("test")

descr = """
test jpackages list/start/stop through processmanager
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "processmanager.jpackages"
enable=True
priority=5

class TEST():

    def setUp(self):
        self.client= j.servers.geventws.getClient("127.0.0.1", 4445, org="myorg", user=j.application.config.get('system.superadmin.login'), \
    passwd=j.application.config.get('gridmaster.superadminpasswd'),category="jpackages")


    def test_jpackagelist(self):
        result=self.client.listJPackages()
        if len(result)<1:
            raise RuntimeError("need to be more than 1 jpackage")

    def test_getJPackage(self):
        result=self.client.getJPackage(domain="jumpscale",name="core")
        if len(result)<>17:            
            raise RuntimeError("need to be 10 fields")
        if not result["name"]=="core":
            raise RuntimeError("Needed to be core")
        
    def test_restartJPackage(self):
        result=self.client.stopJPackage(domain="jumpscale",name="agent")
        j.tools.startupmanager.disableProcess("jumpscale","agent")
        assert j.tools.startupmanager.getStatus4JPackage(j.packages.findNewest(name="agent"))==False
        j.tools.startupmanager.enableProcess("jumpscale","agent")
        result=self.client.startJPackage(domain="jumpscale",name="agent")
        assert j.tools.startupmanager.getStatus4JPackage(j.packages.findNewest(name="agent"))==True

    def test_monitorJPackage(self):
        #@todo stop agent, do monitoring, needs to fail (whcih it doesnt now so bug)
        pass

    def test_existsJPackage(self):
        if self.client.existsJPackage(domain="jumpscale",name="osis")<>True:
            raise RuntimeError("needed to exist")
        try:
            if self.client.existsJPackage(domain="jumpscale",name="osisssss")<>False:
                raise RuntimeError("needed to not exist")
        except Exception,e:
            if str(e).find("Could not find installed jpackage")<>-1:
                return
        raise RuntimeError("jpackage should not have been found")            
