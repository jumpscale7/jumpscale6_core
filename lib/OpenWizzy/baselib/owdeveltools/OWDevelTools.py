from OpenWizzy import o

import OpenWizzy.baselib.screen
import OpenWizzy.grid.grid
class OWDevelTools:

    def __init__(self):
        pass

    def initSystemLocal(self,domain="adomain.com",gridid=0,roles=[]):
        o.core.grid.configureBroker(domain="adomain.com")
        o.core.grid.configureNode(gridid=gridid,roles=roles)

    def startBackendByobu(self,addscreens=[],name="ow"):
        nrworkers=2
        screens=["console","osis","logger","broker" ]+addscreens

        for worker in range(1,nrworkers+1):
            screens.append("w%s"%worker)
      
        #kill remainders
        for item in ["byobu","screen"]:
            cmd="killall %s"%item
            o.system.process.execute(cmd,dieOnNonZeroExitCode=False)

        o.system.platform.screen.createSession(name,screens)

        #start elastic search if needed
        if not o.system.net.tcpPortConnectionTest("127.0.0.1",9200):
            cmd="/etc/init.d/elasticsearch restart"
            o.system.process.execute(cmd)

            #wait for 30 sec on start
            o.system.net.waitConnectionTest("127.0.0.1",9200,30)

        #start osis
        path=o.system.fs.joinPaths("/opt/openwizzy6/apps","osis")
        cmd="cd %s;python osisServerStart.py"%path
        o.system.platform.screen.executeInScreen(name,"osis",cmd,wait=1)

        #start broker
        pathb=o.system.fs.joinPaths("/opt/openwizzy6/apps","broker")
        cmd="cd %s;python zbrokerStart.py"%pathb
        o.system.platform.screen.executeInScreen(name,"broker",cmd,wait=1)

        #start logger
        path=o.system.fs.joinPaths("/opt/openwizzy6/apps","logger")
        cmd="cd %s;python loggerStart.py"%path
        o.system.platform.screen.executeInScreen(name,"logger",cmd,wait=1)

        path=o.system.fs.joinPaths("/opt/openwizzy6/apps","broker")
        for worker in range(1,nrworkers+1):
            roles="system,worker.%s"%worker
            cmd="cd %s;python zworkerStart.py %s %s %s %s"%(path,"127.0.0.1",5556,worker,roles)
            o.system.platform.screen.executeInScreen(name,"w%s"%worker,cmd,wait=1)


        print "* started all required systems"

    def startPortalByobu(self):
        name="owbackend"
        self.startBackendByobu(["ftpgw","portal"],name=name)

        items=o.system.fs.listFilesInDir("/opt/openwizzy6/apps",True,filter="appserver.cfg")
        items=[item.split("/cfg")[0] for item in items]
        items=[item.replace("/opt/openwizzy6/apps/","") for item in items]
        items=[item for item in items if item.find("examples")==-1]
        items=[item for item in items if item.find("portalbase")==-1]
        print "select which portal you would like to start."
        path=o.console.askChoice(items)
        if path==None:
            raise RuntimeError("Could not find a portal, please copy a portan in /opt/openwizzy6/apps/")
        cmd="cd /opt/openwizzy6/apps/%s;python start_appserver.py"%(path)
        o.system.platform.screen.executeInScreen(name,"portal",cmd,wait=1)

        #start ftp
        pathb=o.system.fs.joinPaths("/opt/openwizzy6/apps","portalftpgateway")
        cmd="cd %s;python ftpstart.py"%pathb
        o.system.platform.screen.executeInScreen(name,"ftpgw",cmd,wait=1)

