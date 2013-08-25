from JumpScale import j
from system_contentmanager_osis import *


class system_contentmanager(system_contentmanager_osis):

    """
    this actor manages all content on the wiki
    can e.g. notify wiki/appserver of updates of content
    
    """

    def __init__(self):

        self._te = {}
        self.actorname = "contentmanager"
        self.appname = "system"
        system_contentmanager_osis.__init__(self)

    def getActors(self, **args):
        """
        result list(str) 
        
        """
        return j.core.portal.runningPortal.webserver.actorsloader._objects.keys()

    def getActorsWithPaths(self, **args):
        """
        result list([name,path]) 
        
        """
        actors = []
        for actor in j.core.portal.runningPortal.actorsloader.id2object.keys():
            actor = j.core.portal.runningPortal.actorsloader.id2object[actor]
            actors.append([actor.model.id, actor.model.path])
        return actors

    def getBuckets(self, **args):
        """
        result list(str) 
        
        """
        return j.core.portal.runningPortal.webserver.bucketsloader._objects.keys()

    def getBucketsWithPaths(self, **args):
        """
        result list([name,path]) 
        
        """
        buckets = []
        for bucket in j.core.portal.runningPortal.webserver.bucketsloader.id2object.keys():
            bucket = j.core.portal.runningPortal.webserver.bucketsloader.id2object[bucket]
            buckets.append([bucket.model.id, bucket.model.path])
        return buckets

    def getContentDirsWithPaths(self, **args):
        """
        return root dirs of content (actors,buckets,spaces)
        result list([name,path]) 
        
        """
        objects = []
        for objectname in j.core.portal.runningPortal.webserver.contentdirs.keys():
            objectpath = j.core.portal.runningPortal.webserver.contentdirs[objectname]
            objects.append([objectname, objectpath])
        return objects

    def getSpaces(self, **args):
        """
        result list(str) 
        
        """
        return j.core.portal.runningPortal.webserver.spacesloader.spaces.keys()

    def getSpacesWithPaths(self, **args):
        """
        result list([name,path]) 
        
        """
        spaces = []
        for space in j.core.portal.runningPortal.webserver.spacesloader.spaces.keys():
            space = j.core.portal.runningPortal.webserver.spacesloader.spaces[space]
            spaces.append([space.model.id, space.model.path])
        return spaces

    def modelobjectlist(self, appname, actorname, modelname, key, **args):
        """
        @todo describe what the goal is of this method
        param:appname 
        param:actorname 
        param:modelname 
        param:key         
        """
        actor = j.core.portal.runningPortal.actorsloader.getActor(appname, actorname)
        cache = actor.dbmem.cacheGet(key)
        dtext = j.apps.system.contentmanager.extensions.datatables
        data = dtext.getDataFromActorModel(appname, actorname, modelname, cache["fields"],
                                           cache["fieldids"], cache["fieldnames"])
        return data

    def modelobjectupdate(self, appname, actorname, modelname, key, **args):
        """
        @todo describe what the goal is of this method
        param:appname 
        param:actorname 
        param:modelname 
        param:key 
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method modelobjectupdate")

    def notifyActorDelete(self, id, **args):
        """
        param:id id of space which changed
        result bool 
        
        """
        self.reloadAll(id)

    def reloadAll(self, id):
        def reloadApp():
            print "RELOAD APP FOR ACTORS Delete"
            j.core.portal.runningPortal.reset()

        j.core.portal.runningPortal.actorsloader.id2object.pop(id)

        j.core.portal.runningPortal.scheduler.scheduleFromNow(2, 9, reloadApp)
        j.core.portal.runningPortal.scheduler.scheduleFromNow(10, 9, reloadApp)

    def notifyActorModification(self, id, **args):
        """
        param:id id of actor which changed
        result bool 
        
        """
        loaders = j.core.portal.runningPortal.actorsloader
        loader = loaders.getLoaderFromId(params.id)
        loader.reset()

    def notifyActorNew(self, path, name, **args):
        """
        param:path path of content which got changed
        param:name name
        result bool 
        
        """
        result = False
        key = name.strip().lower()
        # print "name:%s"%name
        if name.find("__") == -1:
            raise RuntimeError("Cannot create actor with name which is not constructed as $appname__$actorname, here %s" % name)
        appname, actorname = name.split("__")
        path = path

        if key not in j.core.portal.runningPortal.actorsloader.actors:
            # actor does not exist yet, create required dirs in basedir
            if path == "":
                path = j.system.fs.joinPaths(j.core.portal.runningPortal.webserver.basepath, "actors", key)
                j.system.fs.createDir(path)
                j.system.fs.createDir(j.system.fs.joinPaths(path, ".actor"))
            else:
                j.system.fs.createDir(path)
                j.system.fs.createDir(j.system.fs.joinPaths(path, ".actor"))

            print "scan path:%s" % path
            j.core.portal.runningPortal.actorsloader.scan(path)
            result = True
        else:
            result = False
        return result

    def notifyActorNewDir(self, actorname, actorpath, path, **args):
        """
        param:actorname 
        param:actorpath 
        param:path 
        
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method notifyActorNewDir")

    def notifyBucketDelete(self, id, **args):
        """
        param:id id of bucket which changed
        result bool 
        
        """
        result = None

        # immediate remove
        loaders = j.core.portal.runningPortal.webserver.bucketsloader
        loaders.removeLoader(id)

        def reloadApp(id=None):
            j.core.portal.runningPortal.webserver.loadSpaces(reset=True)

        # loader.pop(id)
        # j.core.portal.runningPortal.scheduler.scheduleFromNow(1,9,reloadApp,id=id)
        j.core.portal.runningPortal.scheduler.scheduleFromNow(10, 9, reloadApp, id=id)
        return result

    def notifyBucketModification(self, id, **args):
        """
        param:id id of bucket which changed
        result bool 
        
        """
        loaders = j.core.portal.runningPortal.webserver.bucketsloader
        loader = loaders.getLoaderFromId(id)
        loader.reset()

    def notifyBucketNew(self, path, name, **args):
        """
        param:path path of content which got changed
        param:name name
        result bool 
        
        """
        result = False

        key = name.strip().lower()
        path = path

        loader = j.core.portal.runningPortal.webserver.bucketsloader

        if key not in loader.id2object:
            # does not exist yet, create required dirs in basedir
            if path == "":
                path = j.system.fs.joinPaths(j.core.portal.runningPortal.webserver.basepath, "buckets", key)
                j.system.fs.createDir(path)
                j.system.fs.createDir(j.system.fs.joinPaths(path, ".bucket"))
            else:
                j.system.fs.createDir(path)
                j.system.fs.createDir(j.system.fs.joinPaths(path, ".bucket"))

            loader.scan(path)
            result = True
        else:
            result = False

        return result

    def notifyFiledir(self, path, **args):
        """
        param:path path of content which got changed
        result bool 
        
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method notifyFiledir")

    def notifySpaceDelete(self, id, **args):
        """
        param:id id of space which changed
        result bool 
        
        """

        # immediate remove
        loaders = j.core.portal.runningPortal.webserver.spacesloader
        loaders.removeLoader(id)

        def reloadApp():
            print "RELOAD APP SPACE DELETE"
            j.core.portal.runningPortal.webserver.loadSpaces(reset=True)

        # loader=j.core.portal.runningPortal.webserver.spacesloader.id2object
        # loader.pop(id)

        j.core.portal.runningPortal.scheduler.scheduleFromNow(10, 9, reloadApp)

    def notifySpaceModification(self, id, **args):
        """
        param:id id of space which changed
        result bool 
        
        """

        loaders = j.core.portal.runningPortal.webserver.spacesloader
        loader = loaders.getLoaderFromId(id)
        loader.reset()

    def notifySpaceNew(self, path, name, **args):
        """
        param:path path of content which got changed
        param:name name
        result bool 
        
        """
        result = False

        key = name.strip().lower()

        path = path

        loader = j.core.portal.runningPortal.webserver.spacesloader

        if key not in loader.id2object:
            # does not exist yet, create required dirs in basedir
            if path == "":
                path = j.system.fs.joinPaths(j.core.portal.runningPortal.webserver.basepath, "spaces", name)
            else:
                j.system.fs.createDir(path)

            # create default content
            mddir = j.system.fs.joinPaths(path, ".space")
            dest = j.system.fs.joinPaths(path, "%s.wiki" % name)
            j.system.fs.createDir(mddir)
            loader.scan(path)
            source = j.system.fs.joinPaths(mddir, "template.wiki")
            j.system.fs.copyFile(source, dest)
            result = True
        else:
            result = False
        return result

    def notifySpaceNewDir(self, spacename, spacepath, path, **args):
        """
        param:spacename 
        param:spacepath 
        param:path 
        
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method notifySpaceNewDir")

    def prepareActorSpecs(self, app, actor, **args):
        """
        compress specs for specific actor and targz in appropriate download location
        param:app name of app
        param:actor name of actor
        result bool 
        
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method prepareActorSpecs")

    def wikisave(self, authkey, text, **args):
        """
        param:authkey key to authenticate doc
        param:text content of file to edit
        result bool 
        
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method wikisave")
