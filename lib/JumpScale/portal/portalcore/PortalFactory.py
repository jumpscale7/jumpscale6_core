#from ActorsLoaderRemote import ActorsLoaderRemote
from PortalProcess import PortalProcess
from PortalClient import PortalClient
#from ActorLoaderLocal import *

from JumpScale import j


class Group():
    pass


# class GridMap():

#     def __init__(self):
#         self.data = {}  # key is "%s_%s_%s" % (appName, actorName,instance), value=[[ipaddr],port,secret]

#     def _getKey(self, appName, actorName, instance):
#         key = "%s_%s_%s" % (appName.lower().strip(), actorName.lower().strip(), instance)
#         return key

#     def set(self, appName, actorName, instance, ipaddr=None, port=None, secret=None):
#         """
#         @param ipaddr=list of ip addr []
#         """
#         key = self._getKey(appName, actorName, instance)
#         self.data[key] = [ipaddr, port, secret]
#         if not j.core.portal.runningPortal.ismaster:
#             raise RuntimeError("Can only be used local to master appserver")

#     def get(self, appName, actorName, instance):
#         key = self._getKey(appName, actorName, instance)
#         if self.exists(appName, actorName, instance):
#             return self.data[key]
#         else:
#             raise RuntimeError("Cannot find app:%s, actor:%s, instance:%s in gridmap" % (appName, actorName, instance))

#     def exists(self, appName, actorName, instance):
#         key = self._getKey(appName, actorName, instance)
#         return key in self.data


# class GridMapLocal():

#     def __init__(self):
#         raise RuntimeError("gridmap not impl")
#         self.data = {}  # key is "%s_%s_%s" % (appName, actorName,instance), value=[[ipaddr],port,secret]
#         self.datalist = []

#     def _getKey(self, appName, actorName, instance):
#         key = "%s_%s_%s" % (appName.lower().strip(), actorName.lower().strip(), instance)
#         return key

#     def set(self, appName, actorName, instance):
#         """
#         @param ipaddr=list of ip addr []
#         """
#         key = self._getKey(appName, actorName, instance)
#         if j.core.portal.runningPortal == None:
#             raise RuntimeError("can only set to gridmap when appserver is known & operational")
#         ipaddr = j.core.portal.runningPortal.ipaddr
#         if ipaddr == "localhost":
#             ipaddr = "127.0.0.1"
#         port = j.core.portal.runningPortal.port
#         secret = j.core.portal.runningPortal.secret
#         if key not in self.data:
#             self.data[key] = [ipaddr, port, secret]
#             self.datalist.append([appName, actorName, instance, ipaddr, port, secret])

#     def get(self, appName, actorName, instance):
#         key = self._getKey(appName, actorName, instance)
#         if self.exists(appName, actorName, instance):
#             return self.data[key]
#         else:
#             raise RuntimeError("Cannot find app:%s, actor:%s, instance:%s in gridmap" % (appName, actorName, instance))

#     def exists(self, appName, actorName, instance):
#         key = self._getKey(appName, actorName, instance)
#         return key in self.data


class PortalClientFactory():

    def __init__(self):
        self._inited = False
        self.runningPortal = None
        self.inprocess = False
        self._appserverclients = {}

    def loadActorsInProcess(self):
        """
        make sure all actors are loaded on j.apps...
        """
        self.inprocess = True
        self._inited = False
        j.apps = Group()
        j.db.keyvaluestore
        ini = j.tools.inifile.open("cfg/appserver.cfg")
        appdir = ini.getValue("main", "appdir")
        cfgdir = j.system.fs.joinPaths(j.system.fs.getcwd(), "cfg")
        curdir = j.system.fs.getcwd()
        j.system.fs.changeDir(appdir)
        server = PortalProcess(cfgdir=cfgdir, startdir=curdir)

        # for actor in server.actorsloader.actors.keys():
        #     appname,actorname=actor.split("__",1)
        #     print "get actor: %s %s" % (appname,actorname)
        #     try:
        #         server.actorsloader.getActor(appname, actorname)
        #     except Exception,e:
        #         print "*ERROR*: Could not load actor %s %s" % (appname,actorname)

    # def updateGridmap(self):
        #"""
        # this only works when we are not in appserver
        # will make sure all actor clients are recreated #now brute force, can do more intelligent @todo
        #"""
        # if j.core.portal.runningPortal==None:
            # if self.inprocess:
                # j.core.portal.gridmap.data=GridMap()
            # else:
                # result=self.masterClient.wsclient.callWebService("system","manage","getgridmap")
                # gridmap=result[1]["result"]
                # j.core.portal.gridmap.data=gridmap
            # self._appserverclients={}
            # self._actorClients={}
    def getPortalClient(self, ip="localhost", port=9999, secret=None):
        """
        return client to manipulate & access a running application server (out of process)
        caching is done so can call this as many times as required
        secret is normally configured from grid
        there is normally no need to use this method, use self.getActorClient in stead
        """

        if ip == "localhost":
            ip = "127.0.0.1"
        key = "%s_%s" % (ip, port)
        if key in self._appserverclients:
            return self._appserverclients[key]
        else:
            cl = PortalClient(ip, port, secret)
            self._appserverclients[key] = cl
            cl._loadSpaces()
            return cl

    # def getActor(self,appName,actorName,instance=0,authKey=""):
    #     """
    #     get actor (works in process as well as out of process running appserver)
    #     """
    #     self._init()
    #     dbtype=j.enumerators.KeyValueStoreType.FILE_SYSTEM
    #     key="%s_%s" %(appName,actorName)
    #     if self._actors.has_key(key):
    #         return self._actors[key]
    #     else:
    #         if self.inprocess:
    #             if j.apps.__dict__.has_key(appName):
    #                 appgroup=j.apps.__dict__[appName]
    #             else:
    #                 raise RuntimeError("cannot find app for actor %s in %s" % (actorName,path2))
    #             if appgroup.__dict__.has_key(actorName):
    #                 actor=appgroup.__dict__[actorName]
    #             else:
    #                 raise RuntimeError("cannot find actor %s in %s" % (actorName,path2))
    #             return actor
    # else:
    # raise RuntimeError("cannot find actor %s in %s" % (actorName,path2))

    #         else:
    #             master = j.application.shellconfig.appserver.getParam("grid", "master")
    #             secret = j.application.shellconfig.appserver.getParam("grid", "secret")
    # ip=j.application.shellconfig.appserver.getParam("grid","ip")
    #             ws = self.getPortalClient(master, 9000, secret)
    #             code, result = ws.wsclient.callWebService("core", "gridmaster",\
    #                                                       "actorMetadataGet", app=appName, actor=actorName)
    #             loader = ActorsLoaderRemote()
    #             actor = loader.load(appName=appName, actorName=actorName,\
    #                                 metadata=result["metadata"], gridmap=result["gridmap"],\
    #                                 instance=instance, authKey=authKey)
    #         self.actors[key] = actor
    #     return actor

    def usePortalExceptionHandler(self):
        self._init()
        j.core.portal.exceptionHandler = PortalExceptionHandler(
            haltOnError=True)
        return j.core.portal.exceptionHandler

    def getConfigTemplatesPath(self):
        dirname = j.system.fs.getDirName(__file__)
        return j.system.fs.joinPaths(dirname, 'configtemplates')
