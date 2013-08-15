
#from ActorLoaderRemote import ActorLoaderRemote
#from Portal6Process import Portal6Process


from OpenWizzy import o

class PortalProcess():
    pass

class ModelsClass():
    pass

class AppsClass():
    pass


class PortalClient():
    """
    client to appserver 6 running out of process
    """

    def __init__(self,ip,port,secret):
        """
        connect to Portal6
        """
        self.wsclient=o.web.geventws.getClient(ip,port,secret)
        self.ip=ip
        self.port=port
        self.secret=secret

        apsp=PortalProcess()
        o.core.portal.runningPortal = apsp
        apsp.actors={}

    def getActor(self,appname,actorname,instance=0,redis=False,refresh=False):
        if appname.lower()=="system" and actorname=="manage":
            raise RuntimeError("Cannot open actor connection to system actor, use directly the wsclient with callwebservice method.")

        key="%s_%s" % (appname.lower(),actorname.lower())
        if refresh==False and o.core.portal.runningPortal.actors.has_key(key):
            return o.core.portal.runningPortal.actors[key]


        result=self.wsclient.callWebService("system","contentmanager","prepareActorSpecs",app=appname,actor=actorname)
        if result[1] <> None and result[1].has_key("error"):
            error=result[1]["error"]
            raise RuntimeError(error)

        #there is now a tgz specfile ready
        #now we should download
        url="http://%s:%s/files/specs/%s_%s.tgz"%(self.ip,self.port,appname,actorname) #@todo use gridmap
        downloadpathdir=o.system.fs.joinPaths( o.dirs.varDir,"downloadedactorspecs")
        o.system.fs.createDir(downloadpathdir)
        downloadpath=o.system.fs.joinPaths(downloadpathdir,"%s_%s.tgz"%(appname,actorname))
        http=o.clients.http.getConnection()
        http.download(url,downloadpath)
        destinationdir=o.system.fs.joinPaths(downloadpathdir,appname,actorname)
        o.system.fs.removeDirTree(destinationdir)
        o.system.fs.targzUncompress(downloadpath, destinationdir, removeDestinationdir=True)

        codepath=o.system.fs.joinPaths(o.dirs.varDir,"code4appclient",appname,actorname)
        o.core.specparser.parseSpecs(destinationdir,appname=appname,actorname=actorname)



        classs=o.core.codegenerator.getClassActorRemote(appname,actorname,instance=instance,redis=redis,wsclient=self.wsclient,codepath=codepath)

        actorobject=classs()

        modelNames=o.core.specparser.getModelNames(appname,actorname)

        if len(modelNames)>0:
            actorobject.models=ModelsClass()

            for modelName in modelNames:
                classs=o.core.codegenerator.getClassPymodel(appname,actorname,modelName)
                actorobject.models.__dict__[modelName]=o.core.osismodel.getNoDB(appname,actorname,modelName,classs)

        if not o.__dict__.has_key("apps"):
            o.__dict__["apps"]=AppsClass()


        if not o.apps.__dict__.has_key(appname):
            o.apps.__dict__[appname]=AppsClass()

        if not o.apps.__dict__[appname].__dict__.has_key(actorname):
            o.apps.__dict__[appname].__dict__[actorname]=actorobject

        o.core.portal.runningPortal.actors[key]=actorobject

        return actorobject

