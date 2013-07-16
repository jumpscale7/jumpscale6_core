from OpenWizzy import o

from CoreModel.ZNode import ZNode
from CoreModel.ZJob import ZJob
from CoreModel.ZAction import ZAction
from CoreModel.ZApplication import ZApplication
from CoreModel.ZProcess import ZProcess
from CoreModel.ModelObject import ModelObject

from ZDaemonClient import ZDaemonClient
from ZBrokerClientSelfHosted import ZBrokerClientSelfHosted
from ZDaemon import ZDaemon
from ZLogger import ZLogger
from ZLoggerClient import ZLoggerClient
from ZBroker import ZBroker
from ZBrokerClient import ZBrokerClient
from ZWorker import ZWorker
from GeventLoop import GeventLoop
from ZWorkerClient import ZWorkerClient

from LogTargetElasticSearch import LogTargetElasticSearch
import time

class ZCoreModelsFactory():

    def getZNodeObject(self,ddict={},roles=[],name="",netaddr={},machineguid="",id=0):
        """
        @ddict is to directly transform an dict obj to this object = faster, if not given then use the other properties
        """        
        return ZNode(ddict,roles,name,netaddr, machineguid)

    def getZJobObject(self,ddict={},executorrole="",actionid=0,args={},jidmaster=0,jidparent=0,allworkers=True):
        return ZJob(ddict,executorrole,actionid,args=args,jidmaster=jidmaster,jidparent=jidparent,allworkers=allworkers)

    def getZActionObject(self,ddict={},name="",code="",md5="",path="",category="", errordescr="",recoverydescr="", maxtime=0):
        return ZAction(ddict,name,code,md5,path,category, errordescr,recoverydescr, maxtime)

    def getZApplicationObject(self,ddict={},name="",description=""):
        return ZApplication(ddict,name,description)

    def getZProcessObject(self,ddict={},name="",description="",type="",instance=0,systempid=0):
        return ZProcess(ddict,name,description,type,instance,systempid)

    def getModelObject(self, ddict={}):
        return ModelObject(ddict)


class GridFactory():

    def __init__(self):
        self.brokerClient = None
        self.zobjects=ZCoreModelsFactory()
        self._id = None
        self.config = None
        self._bid = None


    def _loadConfig(self):
        if not o.application.__dict__.has_key("config"):
            raise RuntimeWarning("Grid/Broker is not configured please run configureBroker/configureNode first and restart qshell")
        self.config=o.application.config

        if self.config==None:
             raise RuntimeWarning("Grid/Broker is not configured please run configureBroker/configureNode first and restart qshell")

        self.id = self.config.getInt("grid.id")
        self.bid = self.config.getInt("grid.broker.id")
        if self._id == 0:
            o.errorconditionhandler.raiseInputError(msgpub="Grid needs grid id to be filled in in grid config file",message="",category="",die=True)


    def init(self, broker=None):
        """
        """
        self._loadConfig()

        # make sure we only log to stdout
        o.logger.logTargets = []

        o.logger.consoleloglevel=6

        self.nodeobject=o.core.grid.zobjects.getZNodeObject()

        while not self.isbrokerActive(die=False,broker=broker):
            print "Cannot connect to broker, will try again in 1 sec." 
            time.sleep(1)

        self.nid=o.core.grid.config.getInt("node.id")
        if self.bid ==0 or self.nid==0 or o.core.grid.config.get("node.machineguid")=="":
            if broker<>None:
                nodeid2=0
                bid2=broker.id
            else:
                nodeid2,bid2=self.registerNode()
            if self.nid==0:
                self.config.set("node.id", nodeid2)
                self.nid=int(nodeid2)
            if self.bid==0:
                self.config.set("grid.broker.id", bid2)
                self.bid=int(bid2)

        self.aid=self.brokerClient.registerApplication(name=o.application.appname,description="",pid=o.application.whoAmI[2])

        self.processobject=o.core.grid.zobjects.getZProcessObject()
        self.processobject.systempid=o.application.whoAmI[2]

        if self.processobject.name=="":
            self.processobject.name=o.application.appname

        self.pid=self.brokerClient.registerProcess(obj=self.processobject)
        
        self.processobject.id=self.pid
        self.processobject.getSetGuid()

        self.processobject.lastJobId=0

        o.application.initWhoAmI(grid=True)   

        o.logger.consoleloglevel=5
        o.logger.setLogTargetLogForwarder()

    def getLocalIPAccessibleBybroker(self):
        return o.system.net.getReachableIpAddress(self.config.get("grid.broker.ip"), 555)

    def isbrokerLocal(self):
        broker = self.config.get("grid.broker.ip")
        if broker.find("localhost") != -1 or broker.find("127.0.0.1") != -1:
            return True
        else:
            return False

    def isbrokerActive(self, die=True,broker=None):
        """
        @param broker, if given then another connection will be made to the broker
        """

        if broker<>None:
            self.brokerClient =ZBrokerClientSelfHosted(broker)
            return True

        brokerip = self.config.get("grid.broker.ip")
        brokerport = self.config.get("grid.broker.port")

        o.logger.log("Check if broker can be reached on %s:%s."%(brokerip,brokerport), level=6, category="grid.nettest")
        active = o.system.net.tcpPortConnectionTest(brokerip, int(brokerport))

        if active:            
            self.brokerClient = ZBrokerClient(ipaddr=brokerip,port=brokerport)
            pong = self.brokerClient.ping()
            if pong == "pong":
                return True
            # broker.close()

        if die:
            if self.isbrokerLocal():
                o.errorconditionhandler.raiseOperationalCritical(
                    msgpub="broker process cannot be contacted, make sure broker is running & connection settings are configured properly.",
                    message="", category="", die=True, tags="")
            else:
                o.errorconditionhandler.raiseOperationalCritical(message="", category="", msgpub='Cannot find active broker.', die=True, tags="")
        else:
            return False

    def configureBroker(self, domain="adomain.com",osisip="localhost",osisport=5544,brokerid=0):
        """
        @osisnsid = 0 means it will be filled in with unique id coming from osis (a new namespace will be created)
        """
        C = "broker.domain=%s\n"%domain
        C += "broker.osis.ip=%s\n"%osisip
        C += "broker.osis.port=%s\n"%osisport
        C += "broker.id=%s\n"%brokerid
        o.system.fs.createDir(o.system.fs.joinPaths(o.dirs.cfgDir, "grid"))
        path = o.system.fs.joinPaths(o.dirs.cfgDir, "grid", "broker.hrd")
        o.system.fs.writeFile(path, contents=C)


    def registerNode(self):
        o.logger.log("Register node to broker", level=4, category="grid.startup")

        self.nodeobject.machineguid=o.application.getUniqueMachineId().replace(":","")
        znode=self.nodeobject
        o.core.grid.config.set("node.machineguid",znode.machineguid)        
        roles = self.config.get("node.roles").split(",")
        name = self.config.get("node.name")
        netaddr = o.system.net.getNetworkInfo()
        znode.netaddr=netaddr
        znode.name=name
        znode.roles=roles
        nid,bid = self.brokerClient.registerNode(znode)
        o.logger.log("NodeId=%s,BrokerId=%s"%(nid,bid), level=3, category="grid.startup")

        return nid,bid

    def configureNode(self, gridid=0,name="", roles=[], brokerip="localhost",brokerport="5554"):
        """
        create base config files for the node
        """
        if name == "":
            # look for hostname
            name = o.system.net.getHostname()

        C = "node.name=%s\n"%name
        if o.basetype.list.check(roles):
            roles = ",".join(roles)
        C += "node.roles=%s\n"%roles
        C += "node.id=0\n"
        C += "node.machineguid=\n"
        C += "grid.id=%s\n"%gridid
        C += "grid.broker.ip=%s\n"%brokerip
        C += "grid.broker.port=%s\n"%brokerport
        C += "grid.broker.id=0\n"
        o.system.fs.createDir(o.system.fs.joinPaths(o.dirs.cfgDir, "grid"))
        path = o.system.fs.joinPaths(o.dirs.cfgDir, "grid", "node.hrd")
        o.system.fs.writeFile(path, contents=C)

    def initNode(self, name="", roles="*", broker="tcp://localhost:5555"):
        self.configureNode(name, roles, broker)
        o.application.initWhoAmI()
        self._loadConfig()

    def startBroker(self):
        self._loadConfig()
        broker= ZBroker()
        broker.start()

    def getZWorkerClient(self, ipaddr="localhost"):
        self._loadConfig()
        return ZWorkerClient(ipaddr=ipaddr)

    def getZLoggerClient(self,ipaddr="localhost", port=4444):
        return ZLoggerClient(ipaddr=ipaddr,port=port)

    def getZDaemon(self, port=4444,name="",nrCmdGreenlets=50):
        """

        is a generic usable zmq daemon which has a data & cmd channel (data channel not completely implemented for now)
        4444 is the std port for the clientdaemon (DO NOT USE FOR YOUR CUSTOM APPS!!!)
        you can add commands to the deam as follows:

        zd=o.core.grid.getZDaemon(port=5555,nrCmdGreenlets=50)

        class MyCommands():
            def __init__(self,daemon):
                self.daemon=daemon

            def getfreeport(self):
                return self.daemon.getfreeportAndSchedule("datachannelProcessor",self.daemon.loggerGreenlet)

            def log(self,log):
                #in future should use bulk upload feature, now 1 by 1
                print log["message"]

            def pingcmd(self):
                return "pong"

            def echo(self,msg=""):
                return msg

        zd.addCMDsInterface(MyCommands)  #pass as class not as object !!!
        zd.start()

        use self.getZDaemonClientClass as client to this daemon

        """

        return ZDaemon(port=port,name=name,nrCmdGreenlets=nrCmdGreenlets)

    def getZDaemonClientClass(self):
        """
        example usage, see example for server at self.getZDaemon

        ZDaemonClientClass=o.core.grid.getZDaemonClientClass()

        myClient(ZDaemonClientClass):
            def __init__(self,ipaddr):
                ZDaemonClientClass.__init__(self,ipaddr=ipaddr,port=5555)

            def echo(self,msg):
                return self.sendcmd("echo",msg=msg)

        client=myClient()
        client.perftest()
        print client.echo("atest")

        """
        return ZDaemonClient


    def startZWorker(self,addr="localhost",port=5555,instance=0,roles=["all"]):
        """
        #@todo doc
        """
        zw=ZWorker(addr=addr,port=port,instance=instance,roles=roles)
        zw.start()

    def startLocalLogger(self):
        """
        start a local logger daemon which will process logs & events
        """
        d = ZLogger()
        d.start()

    def getLogTargetElasticSearch(self,serverip=None,esclient=None):
        return LogTargetElasticSearch(serverip=serverip,esclient=esclient)

    def getLogTargetOSIS(self):
        return LogTargetOSIS()

    def getGeventLoopClass(self):
        return GeventLoop

