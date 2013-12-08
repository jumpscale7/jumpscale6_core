from JumpScale import j

from CoreModel.ModelObject import ModelObject
import JumpScale.grid.osis
#from ZBrokerClient import ZBrokerClient
from collections import namedtuple

import time


class ZCoreModelsFactory():

    def getModelObject(self, ddict={}):
        return ModelObject(ddict)


class GridFactory():

    def __init__(self):
        self.brokerClient = None
        self.zobjects = ZCoreModelsFactory()
        self.id = None
        self.nid=None
        self.config = None

    def _loadConfig(self,test=True):
        if not j.application.__dict__.has_key("config"):
            raise RuntimeWarning("Grid/Broker is not configured please run configureBroker/configureNode first and restart jshell")
        self.config = j.application.config

        if self.config == None:
            raise RuntimeWarning("Grid/Broker is not configured please run configureBroker/configureNode first and restart jshell")

        self.id = self.config.getInt("grid.id")
        self.nid = self.config.getInt("grid.node.id")

        if test:

            if self.id == 0:
                j.errorconditionhandler.raiseInputError(msgpub="Grid needs grid id to be filled in in grid config file", message="", category="", die=True)

            if self.nid == 0:
                j.errorconditionhandler.raiseInputError(msgpub="Grid needs grid node id (grid.nid) to be filled in in grid config file", message="", category="", die=True)


    def init(self,description="",instance=1):
        """
        """
        print "init grid"
        self._loadConfig(test=False)

        # make sure we only log to stdout
        j.logger.logTargets = []

        j.logger.consoleloglevel = 6

        self.masterip=j.application.config.get("grid.master.ip")

        if not j.system.net.waitConnectionTest(self.masterip,5544,10):
            raise RuntimeError("Could not connect to master osis:%s, maybe master changed (do 'jpackage_configure -n grid_node' to re-init.)"%self.masterip)

        self.gridOsisClient=j.core.osis.getClient(self.masterip)

        if self.nid == 0:
            jp=j.packages.findNewest("jumpscale","grid_node")
            jp.configure()
            self.nid = j.core.grid.config.getInt("grid.nid")

            # self.gridOsisClient.createNamespace(name="system",template="coreobjects",incrementName=False)

            self._loadConfig()

        # self.gridOsisClient.createNamespace(name="system",template="coreobjects",incrementName=False)

        clientprocess=j.core.osis.getClientForCategory(self.gridOsisClient,"system","process")

        clientapplication=j.core.osis.getClientForCategory(self.gridOsisClient,"system","applicationtype")

        obj=clientapplication.new(name=j.application.appname,gid=j.application.whoAmI.gid,type="js",description=description)
        key,new,changed=clientapplication.set(obj)
        obj=clientapplication.get(key)
        aid=obj.id        

        obj2=clientprocess.new(name=j.application.appname,gid=j.application.whoAmI.gid,nid=j.application.whoAmI.nid,\
            systempid=j.application.systempid,\
            aid=aid,instance=instance)
        key,new2,changed2=clientprocess.set(obj2)
        obj=clientprocess.get(key)
        pid=obj.id

        self.pid = pid
        self.processObject=obj

        WhoAmI = namedtuple('WhoAmI', 'gid nid pid')
        j.application.whoAmI = WhoAmI(gid=j.application.whoAmI.gid, nid=j.application.whoAmI.nid, pid=pid)

        j.logger.consoleloglevel = 5

        if j.application.appname<>"logger":
            print "set logtarget forwarder"
            j.logger.setLogTargetLogForwarder()

    def getLocalIPAccessibleByGridMaster(self):
        return j.system.net.getReachableIpAddress(self.config.get("grid.master.ip"), 5544)

    def isGridMasterLocal(self):
        broker = self.config.get("grid.master.ip")
        if broker.find("localhost") != -1 or broker.find("127.0.0.1") != -1:
            return True
        else:
            return False

    def getZBrokerClient(self, addr="127.0.0.1", port=5554, org="myorg", user="root", passwd="1234", ssl=False, category="broker"):
        from ..zdaemon.ZDaemonTransport import ZDaemonTransport
        from JumpScale.grid.serverbase.DaemonClient import DaemonClient
        trans = ZDaemonTransport(addr, port)
        cl = DaemonClient(org=org, user=user, passwd=passwd, ssl=ssl, transport=trans)
        return cl.getCmdClient(category)

    def isbrokerActive(self, die=True, broker=None):
        """
        @param broker, if given then another connection will be made to the broker
        """
        if broker <> None:
            self.brokerClient = broker.daemon.cmdsInterfaces['broker'][0]
            return True

        brokerip = self.config.get("grid.broker.ip")
        brokerport = self.config.get("grid.broker.port")

        j.logger.log("Check if broker can be reached on %s:%s." % (brokerip, brokerport), level=6, category="grid.nettest")
        active = j.system.net.tcpPortConnectionTest(brokerip, int(brokerport))

        if active:
            self.brokerClient = self.getZBrokerClient(addr=brokerip, port=brokerport)
            pong = self.brokerClient.ping()
            if pong == "pong":
                return True
            # broker.close()

        if die:
            if self.isbrokerLocal():
                j.errorconditionhandler.raiseOperationalCritical(
                    msgpub="broker process cannot be contacted, make sure broker is running & connection settings are configured properly.",
                    message="", category="", die=True, tags="")
            else:
                j.errorconditionhandler.raiseOperationalCritical(message="", category="", msgpub='Cannot find active broker.', die=True, tags="")
        else:
            return False

    def configureBroker(self, domain="adomain.com", osisip="localhost", osisport=5544, brokerid=0):
        """
        @osisnsid = 0 means it will be filled in with unique id coming from osis (a new namespace will be created)
        """
        C = "broker.domain=%s\n" % domain
        C += "broker.osis.ip=%s\n" % osisip
        C += "broker.osis.port=%s\n" % osisport
        C += "broker.id=%s\n" % brokerid
        j.system.fs.createDir(j.system.fs.joinPaths(j.dirs.cfgDir, "grid"))
        path = j.system.fs.joinPaths(j.dirs.cfgDir, "grid", "broker.hrd")
        j.system.fs.writeFile(path, contents=C)

    def startBroker(self):
        from ZBroker import ZBroker
        self._loadConfig()
        broker = ZBroker()
        broker.start()

    def getZWorkerClient(self, ipaddr="localhost"):
        self._loadConfig()
        from ZWorkerClient import ZWorkerClient
        return ZWorkerClient(ipaddr=ipaddr)

    def getZLoggerClient(self, ipaddr="localhost", port=4443):
        from ZLoggerClient import ZLoggerClient
        return ZLoggerClient(ipaddr=ipaddr, port=port)

    def startZWorker(self, addr="localhost", port=5651, instance=0, roles=["*"]):
        """
        #@todo doc
        """
        from ZWorker import ZWorker
        zw = ZWorker(addr=addr, port=port, instance=instance, roles=roles)
        zw.start()

    def startLocalLogger(self):
        """
        start a local logger daemon which will process logs & events
        """
        from ZLogger import ZLogger
        d = ZLogger()
        d.start()

    def getLogTargetElasticSearch(self, serverip=None, esclient=None):
        from LogTargetElasticSearch import LogTargetElasticSearch
        return LogTargetElasticSearch(serverip=serverip, esclient=esclient)

    def getLogTargetOSIS(self):
        return LogTargetOSIS()
