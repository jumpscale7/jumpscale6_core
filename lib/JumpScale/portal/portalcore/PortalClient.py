
#from ActorLoaderRemote import ActorLoaderRemote
#from Portal6Process import Portal6Process


from JumpScale import j


class PortalProcess():
    pass


class ModelsClass():
    pass


class GroupAppsClass(object):
    def __init__(self, client):
        self._client = client

    def __getattr__(self, appname):
        app = AppClass(self._client, appname)
        setattr(self, appname, app)
        return app

class AppClass(object):
    def __init__(self, client, appname):
        self._appname = appname
        self._client = client

    def __getattr__(self, actorname):
        if actorname in ('__members__', '__methods__', 'trait_names', '_getAttributeNames'):
            return object.__getattr__(self, actorname)
        actor = self._client.getActor(self._appname, actorname)
        setattr(self, actorname, actor)
        return actor

class PortalClient():

    """
    client to appserver 6 running out of process
    """

    def __init__(self, ip, port, secret):
        """
        connect to Portal6
        """
        self.wsclient = j.web.geventws.getClient(ip, port, secret)
        self.ip = ip
        self.port = port
        self.secret = secret

        apsp = PortalProcess()
        j.core.portal.runningPortal = apsp
        apsp.actors = {}

        if "apps" not in j.__dict__:
            j.__dict__["apps"] = GroupAppsClass(self)

    def getActor(self, appname, actorname, instance=0, redis=False, refresh=False):
        if appname.lower() == "system" and actorname == "manage":
            raise RuntimeError("Cannot open actor connection to system actor, use directly the wsclient with callwebservice method.")

        key = "%s_%s" % (appname.lower(), actorname.lower())
        if refresh == False and key in j.core.portal.runningPortal.actors:
            return j.core.portal.runningPortal.actors[key]

        result = self.wsclient.callWebService("system", "contentmanager", "prepareActorSpecs", app=appname, actor=actorname)
        if result[1] != None and "error" in result[1]:
            error = result[1]["error"]
            raise RuntimeError(error)

        # there is now a tgz specfile ready
        # now we should download
        url = "http://%s:%s/files/specs/%s_%s.tgz" % (self.ip, self.port, appname, actorname)  # @todo use gridmap
        downloadpathdir = j.system.fs.joinPaths(j.dirs.varDir, "downloadedactorspecs")
        j.system.fs.createDir(downloadpathdir)
        downloadpath = j.system.fs.joinPaths(downloadpathdir, "%s_%s.tgz" % (appname, actorname))
        http = j.clients.http.getConnection()
        http.download(url, downloadpath)
        destinationdir = j.system.fs.joinPaths(downloadpathdir, appname, actorname)
        j.system.fs.removeDirTree(destinationdir)
        j.system.fs.targzUncompress(downloadpath, destinationdir, removeDestinationdir=True)

        codepath = j.system.fs.joinPaths(j.dirs.varDir, "code4appclient", appname, actorname)
        j.core.specparser.parseSpecs(destinationdir, appname=appname, actorname=actorname)

        classs = j.core.codegenerator.getClassActorRemote(appname, actorname, instance=instance, redis=redis, wsclient=self.wsclient, codepath=codepath)

        actorobject = classs()

        modelNames = j.core.specparser.getModelNames(appname, actorname)
        j.core.codegenerator.setTarget('client')

        if len(modelNames) > 0:
            actorobject.models = ModelsClass()

            for modelName in modelNames:
                classs = j.core.codegenerator.getClassPymodel(appname, actorname, modelName)
                actorobject.models.__dict__[modelName] = j.core.osismodel.getNoDB(appname, actorname, modelName, classs)

        j.core.portal.runningPortal.actors[key] = actorobject

        return actorobject
