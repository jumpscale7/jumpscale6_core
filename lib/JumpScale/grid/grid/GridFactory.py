from JumpScale import j

from CoreModel.ModelObject import ModelObject
import JumpScale.grid.osis
#from ZBrokerClient import ZBrokerClient
from collections import namedtuple
import JumpScale.grid.geventws
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
        self.roles = list()

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

        ##SEEMS TO BE OUTDATED CODE !!!!!
        ##we have pid information in redis now, & processmaanager should react with that

        # self.masterip=j.application.config.get("grid.master.ip")
        # roles = list()
        # if self.config.exists("grid.node.roles"):
        #     roles = j.application.config.getList('grid.node.roles')
        # roles = [ role.lower() for role in roles ]
        # if self.isGridMasterLocal():
        #     if 'master' not in roles:
        #         roles.append('master')
        # self.roles = roles


        # if not j.system.net.waitConnectionTest(self.masterip,5544,10):
        #     raise RuntimeError("Could not connect to master osis (%s:%s)"%(self.masterip,5544))

        # self.gridOsisClient=j.core.osis.getClient(self.masterip, user='root')

        # if self.nid == 0:
        #     jp=j.packages.findNewest("jumpscale","grid_node")
        #     jp.configure()
        #     self.nid = j.core.grid.config.getInt("grid.node.id")

        #     # self.gridOsisClient.createNamespace(name="system",template="coreobjects",incrementName=False)

        #     self._loadConfig()

        # # self.gridOsisClient.createNamespace(name="system",template="coreobjects",incrementName=False)

        # clientprocess=j.core.osis.getClientForCategory(self.gridOsisClient,"system","process")

        # ps=j.system.process.getProcessObject(j.application.systempid)
        # workingdir=ps.getcwd()

        # if False:#j.system.net.tcpPortConnectionTest("127.0.0.1",4445):  #@todo to fix later
        #     #means there is a process manager, we can ask the pid
        #     clientpm=j.servers.geventws.getClient("127.0.0.1", 4445, org="myorg", user="root", \
        #         passwd="",category="process")
        #     if j.application.appname.find(":")<>-1:
        #         #domain & sname known
        #         domain,name=j.application.appname.split(":")
        #     else:
        #         domain=None
        #         name=j.application.appname
            
        #     grid_guid=clientpm.registerProcess(j.application.systempid,domain,name,workingdir=workingdir)
        #     grid_pid=int(grid_guid.split("_")[1])

        # else:
        #     obj2=clientprocess.new(name=j.application.appname,gid=j.application.whoAmI.gid,\
        #         nid=j.application.whoAmI.nid,\
        #         systempid=j.application.systempid,\
        #         instance=instance)
        #     obj2.workingdir=workingdir


        #     grid_guid,new2,changed2=clientprocess.set(obj2)
        #     grid_pid=int(grid_guid.split("_")[1])

        # self.pid = grid_pid

        # WhoAmI = namedtuple('WhoAmI', 'gid nid pid')
        # j.application.whoAmI = WhoAmI(gid=j.application.whoAmI.gid, nid=j.application.whoAmI.nid, pid=grid_pid)

        j.logger.consoleloglevel = 5

        if j.application.appname<>"logger":
            print "set logtarget forwarder"
            j.logger.setLogTargetLogForwarder()

    def getLocalIPAccessibleByGridMaster(self):
        return j.system.net.getReachableIpAddress(self.config.get("grid.master.ip"), 5544)

    def isGridMasterLocal(self):
        broker = self.config.get("grid.master.ip")
        return j.system.net.isIpLocal(broker)

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
            self.brokerClient = broker.daemon.cmdsInterfaces['broker']
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
