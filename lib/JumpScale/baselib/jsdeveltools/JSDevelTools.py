from JumpScale import j

import JumpScale.baselib.screen

class JSDevelTools:

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

        #start osis
        print '* Starting osis'
        path=j.system.fs.joinPaths("/opt/jumpscale/apps","osis")
        cmd="cd %s;python osisServerStart.py"%path
        j.system.platform.screen.executeInScreen(name,"osis",cmd,wait=1)
        if not j.system.net.waitConnectionTest('localhost', 5544, 30):
            raise RuntimeError("Failed to start osis server")

        #start broker
        print '* Starting broker'
        pathb=j.system.fs.joinPaths("/opt/jumpscale/apps","broker")
        cmd="cd %s;python zbrokerStart.py"%pathb
        j.system.platform.screen.executeInScreen(name,"broker",cmd,wait=1)

        #start logger
        print '* Starting logger'
        path=j.system.fs.joinPaths("/opt/jumpscale/apps","logger")
        cmd="cd %s;python loggerStart.py"%path
        j.system.platform.screen.executeInScreen(name,"logger",cmd,wait=1)
        if not j.system.net.waitConnectionTest('localhost', 4444, 30):
            raise RuntimeError("Failed to start logger server")

        # print '* Starting workers'
        # path=j.system.fs.joinPaths("/opt/jumpscale/apps","broker")
        # for worker in range(1,nrworkers+1):
        #     roles="system,worker.%s"%worker
        #     cmd="cd %s;python zworkerStart.py %s %s %s %s"%(path,"127.0.0.1",6556,worker,roles)
        #     j.system.platform.screen.executeInScreen(name,"w%s"%worker,cmd,wait=1)

    def startPortalByobu(self, path=None):
        name="owbackend"
        self.startBackendByobu(["ftpgw","portal"],name=name)

        if not path: #to enable startPortal to work non-interactively as well
            items=j.system.fs.listFilesInDir("/opt/jumpscale/apps",True,filter="appserver.cfg")
            items=[item.split("/cfg")[0] for item in items]
            items=[item.replace("/opt/jumpscale/apps/","") for item in items]
            items=[item for item in items if item.find("examples")==-1 and item.find("portalbase") == -1]
            print "select which portal you would like to start."
            path=j.console.askChoice(items)
        if path==None:
            raise RuntimeError("Could not find a portal, please copy a portal in /opt/jumpscale/apps/")

        print '* Starting portal'
        cmd="cd /opt/jumpscale/apps/%s;python portal_start.py"%(path)
        j.system.platform.screen.executeInScreen(name,"portal",cmd,wait=1)
        if not j.system.net.waitConnectionTest('localhost', 9999, 30):
            raise RuntimeError("Failed to start portal")

        #start ftp
        print '* Starting ftpgw'
        pathb=j.system.fs.joinPaths("/opt/jumpscale/apps","portalftpgateway")
        cmd="cd %s;python ftpstart.py"%pathb
        j.system.platform.screen.executeInScreen(name,"ftpgw",cmd,wait=1)
        if not j.system.net.waitConnectionTest('localhost', 21, 30):
            raise RuntimeError("Failed to start ftp")

