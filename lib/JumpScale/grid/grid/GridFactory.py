from JumpScale import j

from CoreModel.ModelObject import ModelObject

#from ZBrokerClient import ZBrokerClient

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
        self.nid = self.config.getInt("grid.nid")

        if test:

            if self.id == 0:
                j.errorconditionhandler.raiseInputError(msgpub="Grid needs grid id to be filled in in grid config file", message="", category="", die=True)

            if self.nid == 0:
                j.errorconditionhandler.raiseInputError(msgpub="Grid needs grid node id (grid.nid) to be filled in in grid config file", message="", category="", die=True)


    def init(self, broker=None):
        """
        """

        self._loadConfig(test=False)

        # make sure we only log to stdout
        j.logger.logTargets = []

        j.logger.consoleloglevel = 6

        self.masterip=j.application.config.get("grid.master.ip")

        if not j.system.net.waitConnectionTest(self.masterip,5544,10):
            raise RuntimeError("Could not connect to master osis")

        if self.nid == 0:
            jp=j.packages.findNewest("jumpscale","grid_node")
            jp.configure()
            self.nid = j.core.grid.config.getInt("grid.nid")

            self._loadConfig()

        from IPython import embed
        print "DEBUG NOW init grid"
        embed()

        #register application
        self.aid = self.brokerClient.registerApplication(name=j.application.appname, description="", pid=j.application.whoAmI[2])

        self.processobject = j.core.grid.zobjects.getZProcessObject()
        self.processobject.systempid = j.application.whoAmI[2]

        if self.processobject.name == "":
            self.processobject.name = j.application.appname

        self.pid = self.brokerClient.registerProcess(obj=self.processobject.__dict__)

        self.processobject.id = self.pid
        self.processobject.getSetGuid()

        self.processobject.lastJobId = 0

        j.application.initWhoAmI(grid=True)

        j.logger.consoleloglevel = 5
        j.logger.setLogTargetLogForwarder()

    def getLocalIPAccessibleBybroker(self):
        return j.system.net.getReachableIpAddress(self.config.get("grid.broker.ip"), 555)

    def isbrokerLocal(self):
        broker = self.config.get("grid.broker.ip")
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

    def getZLoggerClient(self, ipaddr="localhost", port=4444):
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
