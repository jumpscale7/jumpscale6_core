from OpenWizzy import o

import OpenWizzy.baselib.screen
import OpenWizzy.grid.grid

class OWDevelTools:

    def __init__(self):
        pass

    def initSystemLocal(self,domain="adomain.com",gridid=0,roles=[]):
        o.core.grid.configureBroker(domain="adomain.com")
        o.core.grid.configureNode(gridid=gridid,roles=roles)

    def startBackendByobu(self):
        nrworkers=0
        nrclients=0
        screens=["console","osis","logger","broker" ]
        for worker in range(1,nrworkers+1):
            screens.append("w%s"%worker)
        for client in range(1,nrclients+1):
            screens.append("c%s"%client)
        
        #kill remainders
        for item in ["byobu","screen"]:
            cmd="killall %s"%item
            o.system.process.execute(cmd,dieOnNonZeroExitCode=False)

        o.system.platform.screen.createSession("broker",screens)

        #start elastic search
        cmd="/etc/init.d/elasticsearch restart"
        o.system.process.execute(cmd)

        #wait for 30 sec on start
        o.system.net.waitConnectionTest("127.0.0.1",9200,30)

        #start osis
        path=o.system.fs.joinPaths("/opt/openwizzy6/apps","osis")
        cmd="cd %s;python osisServerStart.py"%path
        o.system.platform.screen.executeInScreen("broker","osis",cmd,wait=1)

        #start logger
        path=o.system.fs.joinPaths("/opt/openwizzy6/apps","logger")
        cmd="cd %s;python loggerStart.py"%path
        o.system.platform.screen.executeInScreen("broker","logger",cmd,wait=1)

        #start broker
        pathb=o.system.fs.joinPaths("/opt/openwizzy6/apps","broker")
        cmd="cd %s;python zbrokerStart.py"%pathb
        o.system.platform.screen.executeInScreen("broker","broker",cmd,wait=1)

        for worker in range(1,nrworkers+1):
            cmd="python zworkerStart.py %s %s %s %s"%(host,port,worker,"system/%s,*"%nodeid)
            o.system.platform.screen.executeInScreen("broker","w%s"%worker,cmd,wait=1)

        for client in range(1,nrclients+1):
            cmd="python zclienttest.py %s %s %s %s"%(host,portbroker,client,nrtestsperclient)
            o.system.platform.screen.executeInScreen("broker","c%s"%client,cmd,wait=1)

        print "* started all required systems"

    def startPortalByobu(self):
        items=o.system.fs.listFilesInDir("/opt/openwizzy6/apps",True,filter="appserver.cfg")
        items=[item.split("/cfg")[0] for item in items]
        items=[item.replace("/opt/openwizzy6/apps/","") for item in items]
        path=o.console.askChoice(items)
        cmd="cd %s;python start_appserver.py"%(path)
        o.system.platform.screen.executeInScreen("portal","c%s"%client,cmd,wait=1)
