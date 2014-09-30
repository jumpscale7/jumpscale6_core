#from ActorsLoaderRemote import ActorsLoaderRemote
from PortalServer import PortalServer
from PortalClient import PortalClient
#from ActorLoaderLocal import *

import JumpScale.baselib.redis

from JumpScale import j


class Group():
    pass


class PortalFactory():

    def __init__(self):
        # self._inited = False
        self.active = None
        self.inprocess = False
        self._portalClients = {}

    def getServer(self,hrd):
        return PortalServer(hrd)

    # def getPortalConfig(self, appname):
    #     cfg = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', appname, 'cfg', 'portal')
    #     return j.config.getConfig(cfg)

    def loadActorsInProcess(self):
        """
        make sure all actors are loaded on j.apps...
        """
        raise RuntimeError("not implemented, need to fix")
        self.inprocess = True
        # self._inited = False
        j.apps = Group()
        j.db.keyvaluestore
        ini = j.tools.inifile.open("cfg/appserver.cfg")
        appdir = ini.getValue("main", "appdir")
        appdir=appdir.replace("$base",j.dirs.baseDir)
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

    def getClientByInstance(self, instance=None):
        if not instance:
            instance = j.application.hrdinstance.get('portal.connection')
        jp = j.packages.findNewest('jumpscale', 'portal_client')
        jp.load(instance)
        addr = jp.hrd_instance.get('addr')
        port = jp.hrd_instance.getInt('port')
        secret = jp.hrd_instance.getInt('secret')
        return self.getClient(addr, port, secret)

    def getClient(self, ip="localhost", port=9900, secret=None):
        """
        return client to manipulate & access a running application server (out of process)
        caching is done so can call this as many times as required
        secret is normally configured from grid
        there is normally no need to use this method, use self.getActorClient in stead
        """

        if ip == "localhost":
            ip = "127.0.0.1"
        key = "%s_%s_%s" % (ip, port,secret)
        if key in self._portalClients:
            return self._portalClients[key]
        else:
            cl = PortalClient(ip, port, secret)
            self._portalClients[key] = cl
            # cl._loadSpaces()
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

    # def usePortalExceptionHandler(self):
    #     self._init()
    #     j.core.portal.exceptionHandler = PortalExceptionHandler(
    #         haltOnError=True)
    #     return j.core.portal.exceptionHandler

    # def getConfigTemplatesPath(self):
    #     dirname = j.system.fs.getDirName(__file__)
    #     return j.system.fs.joinPaths(dirname, 'configtemplates')
