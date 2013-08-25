from JumpScale import j

import JumpScale.baselib.screen

class OWDevelTools:

    def __init__(self):
        pass

    def initSystemLocal(self,domain="adomain.com",gridid=0,roles=[]):
        import JumpScale.grid
        j.core.grid.configureBroker(domain="adomain.com")
        j.core.grid.configureNode(gridid=gridid,roles=roles)

    def startBackendByobu(self,addscreens=[],name="ow"):
        nrworkers=2
        screens=["console","osis","logger","broker" ]+addscreens

        for worker in range(1,nrworkers+1):
            screens.append("w%s"%worker)
      
        #kill remainders
        for item in ["byobu","screen"]:
            cmd="killall %s"%item
            j.system.process.execute(cmd,dieOnNonZeroExitCode=False)

        j.system.platform.screen.createSession(name,screens)

        #start elastic search if needed
        if not j.system.net.tcpPortConnectionTest("127.0.0.1",9200):
            cmd="/etc/init.d/elasticsearch restart"
            j.system.process.execute(cmd)

            #wait for 30 sec on start
            j.system.net.waitConnectionTest("127.0.0.1",9200,30)

        #start osis
        path=j.system.fs.joinPaths("/opt/jumpscale/apps","osis")
        cmd="cd %s;python osisServerStart.py"%path
        j.system.platform.screen.executeInScreen(name,"osis",cmd,wait=1)

        #start broker
        pathb=j.system.fs.joinPaths("/opt/jumpscale/apps","broker")
        cmd="cd %s;python zbrokerStart.py"%pathb
        j.system.platform.screen.executeInScreen(name,"broker",cmd,wait=1)

        #start logger
        path=j.system.fs.joinPaths("/opt/jumpscale/apps","logger")
        cmd="cd %s;python loggerStart.py"%path
        j.system.platform.screen.executeInScreen(name,"logger",cmd,wait=1)

        path=j.system.fs.joinPaths("/opt/jumpscale/apps","broker")
        for worker in range(1,nrworkers+1):
            roles="system,worker.%s"%worker
            cmd="cd %s;python zworkerStart.py %s %s %s %s"%(path,"127.0.0.1",5556,worker,roles)
            j.system.platform.screen.executeInScreen(name,"w%s"%worker,cmd,wait=1)


        print "* started all required systems"

    def startPortalByobu(self, path=None):
        j.application.shellconfig.interactive=True
        name="owbackend"
        self.startBackendByobu(["ftpgw","portal"],name=name)

        items=j.system.fs.listFilesInDir("/opt/jumpscale/apps",True,filter="appserver.cfg")
        items=[item.split("/cfg")[0] for item in items]
        items=[item.replace("/opt/jumpscale/apps/","") for item in items]
        items=[item for item in items if item.find("examples")==-1]
        items=[item for item in items if item.find("portalbase")==-1]
        if not path: #to enable startPortal to work non-interactively as well
            print "select which portal you would like to start."
            path=j.console.askChoice(items)
        if path==None:
            raise RuntimeError("Could not find a portal, please copy a portan in /opt/jumpscale/apps/")
        cmd="cd /opt/jumpscale/apps/%s;python start_appserver.py"%(path)
        j.system.platform.screen.executeInScreen(name,"portal",cmd,wait=1)

        #start ftp
        pathb=j.system.fs.joinPaths("/opt/jumpscale/apps","portalftpgateway")
        cmd="cd %s;python ftpstart.py"%pathb
        j.system.platform.screen.executeInScreen(name,"ftpgw",cmd,wait=1)

