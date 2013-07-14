from OpenWizzy import o
from system_contentmanager_osis import system_contentmanager_osis

class system_contentmanager(system_contentmanager_osis):
    """
    this actor manages all content on the wiki
    can e.g. notify wiki/appserver of updates of content
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="contentmanager"
        self.appname="system"
        system_contentmanager_osis.__init__(self)
    
    def getActors(self,**args):
        """
        result list(str) 
        
        """
        return o.core.portal.runningPortal.webserver.actorsloader._objects.keys()    

    def getActorsWithPaths(self,**args):
        """
        result list([name,path]) 
        
        """
        actors=[]
        for actor in o.core.portal.runningPortal.actorsloader.id2object.keys():
            actor=o.core.portal.runningPortal.actorsloader.id2object[actor]
            actors.append([actor.model.id,actor.model.path])
        return actors
    

    def getBuckets(self,**args):
        """
        result list(str) 
        
        """
        return o.core.portal.runningPortal.webserver.bucketsloader._objects.keys()

    def getBucketsWithPaths(self,**args):
        """
        result list([name,path]) 
        
        """
        buckets=[]
        for bucket in o.core.portal.runningPortal.webserver.bucketsloader.id2object.keys():
            bucket=o.core.portal.runningPortal.webserver.bucketsloader.id2object[bucket]
            buckets.append([bucket.model.id,bucket.model.path])
        return buckets

    def getContentDirsWithPaths(self,**args):
        """
        return root dirs of content (actors,buckets,spaces)
        result list([name,path]) 
        
        """
        objects=[]
        for objectname in o.core.portal.runningPortal.webserver.contentdirs.keys():
            objectpath=o.core.portal.runningPortal.webserver.contentdirs[objectname]
            objects.append([objectname,objectpath])
        return objects
    

    def getSpaces(self,**args):
        """
        result list(str) 
        
        """
        return o.core.portal.runningPortal.webserver.spacesloader.spaces.keys()
    

    def getSpacesWithPaths(self,**args):
        """
        result list([name,path]) 
        
        """
        spaces=[]
        for space in o.core.portal.runningPortal.webserver.spacesloader.spaces.keys():
            space=o.core.portal.runningPortal.webserver.spacesloader.spaces[space]
            spaces.append([space.model.id,space.model.path])
        return spaces
    

    def modelobjectlist(self,appname,actorname,modelname,key,**args):
        """
        @todo describe what the goal is of this method
        param:appname 
        param:actorname 
        param:modelname 
        param:key         
        """
        actor=o.core.portal.runningPortal.actorsloader.getActor(appname,actorname)     
        cache=actor.dbmem.cacheGet(key)
        
        dtext=q.apps.system.contentmanager.extensions.datatables
        data=dtext.getDataFromActorModel(appname,actorname,modelname,cache["fields"],\
            cache["fieldids"],cache["fieldnames"])

        return data

    def modelobjectupdate(self,appname,actorname,key,**args):
        """
        post args with ref_$id which refer to the key which is stored per actor in the cache
        param:appname 
        param:actorname 
        param:key 
        result html 
        
        """
        actor=q.apps.__dict__[appname].__dict__[actorname]
        ctx=args["ctx"]
        data=actor.dbmem.cacheGet("form_%s"%key)
        for ref in [item for item in ctx.params.keys() if item.find("ref")==0]:
            ref0=int(ref.replace("ref_",""))
            key,refS=data[1][ref0]  #@ref is how to retrieve info from the object
            model=data[0][key]
            exec("model.%s=args[\"%s\"]"%(refS,ref))

        for modelkey in data[0].keys():
            model=data[0][modelkey]
            exec("actor.model_%s_set(model)"%model._meta[2])
        if 'HTTP_REFERER' in ctx.env:
            headers = [('Location', ctx.env['HTTP_REFERER'])]
            ctx.start_response('302', headers)

    def notifyActorDelete(self,id,**args):
        """
        param:id id of space which changed
        result bool 
        
        """
        self.reloadAll(id)

    def bitbucketreload(self, spacename, **args):
        import os
        s = os.getcwd()
        path = s.split('/apps/')[0]
        mc = q.clients.mercurial.getClient(path)
        mc.pullupdate()
        if spacename != 'None':
            o.core.portal.runningPortal.webserver.loadSpace(spacename)
        else:
            o.core.portal.runningPortal.webserver.loadSpace(self.appname)
        return []

    def reloadAll(self,id):
        def reloadApp():
            print "RELOAD APP FOR ACTORS Delete"
            o.core.portal.runningPortal.reset()

        o.core.portal.runningPortal.actorsloader.id2object.pop(id)

        o.core.portal.runningPortal.scheduler.scheduleFromNow(2,9,reloadApp)
        o.core.portal.runningPortal.scheduler.scheduleFromNow(10,9,reloadApp)
    

    def notifyActorModification(self,id,**args):
        """
        param:id id of actor which changed
        result bool 
        
        """
        loaders=o.core.portal.runningPortal.actorsloader
        loader=loaders.getLoaderFromId(params.id)
        loader.reset()
    

    def notifyActorNew(self,path,name,**args):
        """
        param:path path of content which got changed
        param:name name
        result bool 
        
        """
        result=False
        key=name.strip().lower()
        #print "name:%s"%name
        if name.find("__")==-1:
            raise RuntimeError("Cannot create actor with name which is not constructed as $appname__$actorname, here %s"%name)
        appname,actorname=name.split("__")
        path=path

        if not o.core.portal.runningPortal.actorsloader.actors.has_key(key):
            #actor does not exist yet, create required dirs in basedir
            if path=="":
                path=o.system.fs.joinPaths(o.core.portal.runningPortal.webserver.basepath,"actors",key)
                o.system.fs.createDir(path)
                o.system.fs.createDir(o.system.fs.joinPaths(path,".actor"))
            else:
                o.system.fs.createDir(path)
                o.system.fs.createDir(o.system.fs.joinPaths(path,".actor"))
                
            print "scan path:%s"%path
            o.core.portal.runningPortal.actorsloader.scan(path)
            result=True
        else:
            result=False  
        return result  

    def notifyActorNewDir(self,actorname,actorpath,path,**args):
        """
        param:actorname 
        param:actorpath 
        param:path 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyActorNewDir")
    

    def notifyBucketDelete(self,id,**args):
        """
        param:id id of bucket which changed
        result bool 
        
        """
        result=None

        #immediate remove
        loaders=o.core.portal.runningPortal.webserver.bucketsloader
        loaders.removeLoader(id)
        
        def reloadApp(id=None):        
            o.core.portal.runningPortal.webserver.loadSpaces(reset=True)

        #loader.pop(id)
        # o.core.portal.runningPortal.scheduler.scheduleFromNow(1,9,reloadApp,id=id)
        o.core.portal.runningPortal.scheduler.scheduleFromNow(10,9,reloadApp,id=id)
        return result
        

    def notifyBucketModification(self,id,**args):
        """
        param:id id of bucket which changed
        result bool 
        
        """
        loaders=o.core.portal.runningPortal.webserver.bucketsloader
        loader=loaders.getLoaderFromId(id)
        loader.reset()

    

    def notifyBucketNew(self,path,name,**args):
        """
        param:path path of content which got changed
        param:name name
        result bool 
        
        """
        result=False

        key=name.strip().lower()
        path=path

        loader=o.core.portal.runningPortal.webserver.bucketsloader

        if not loader.id2object.has_key(key):
            #does not exist yet, create required dirs in basedir
            if path=="":
                path=o.system.fs.joinPaths(o.core.portal.runningPortal.webserver.basepath,"buckets",key)
                o.system.fs.createDir(path)
                o.system.fs.createDir(o.system.fs.joinPaths(path,".bucket"))
            else:
                o.system.fs.createDir(path)
                o.system.fs.createDir(o.system.fs.joinPaths(path,".bucket"))
                
            loader.scan(path)
            result=True
        else:
            result=False

        return result
    

    def notifyFiledir(self,path,**args):
        """
        param:path path of content which got changed
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyFiledir")
    

    def notifySpaceDelete(self,id,**args):
        """
        param:id id of space which changed
        result bool 
        
        """

        #immediate remove
        loaders=o.core.portal.runningPortal.webserver.spacesloader
        loaders.removeLoader(id)
        
        def reloadApp():
            print "RELOAD APP SPACE DELETE"
            o.core.portal.runningPortal.webserver.loadSpaces(reset=True)

        # loader=o.core.portal.runningPortal.webserver.spacesloader.id2object
        # loader.pop(id)

        o.core.portal.runningPortal.scheduler.scheduleFromNow(10,9,reloadApp)

    

    def notifySpaceModification(self,id,**args):
        """
        param:id id of space which changed
        result bool 
        
        """

        loaders=o.core.portal.runningPortal.webserver.spacesloader
        loader=loaders.getLoaderFromId(id)
        loader.reset()
    
    

    def notifySpaceNew(self,path,name,**args):
        """
        param:path path of content which got changed
        param:name name
        result bool 
        
        """
        result=False

        key=name.strip().lower()

        path=path

        loader=o.core.portal.runningPortal.webserver.spacesloader

        if not loader.id2object.has_key(key):
            #does not exist yet, create required dirs in basedir
            if path=="":
                path=o.system.fs.joinPaths(o.core.portal.runningPortal.webserver.basepath,"spaces",name)            
            else:
                o.system.fs.createDir(path)
                
            #create default content
            mddir=o.system.fs.joinPaths(path,".space")
            dest=o.system.fs.joinPaths(path,"%s.wiki"%name)
            o.system.fs.createDir(mddir)                
            loader.scan(path)
            source=o.system.fs.joinPaths(mddir,"template.wiki")
            o.system.fs.copyFile(source,dest)
            result=True
        else:
            result=False
        return result
    

    def notifySpaceNewDir(self,spacename,spacepath,path,**args):
        """
        param:spacename 
        param:spacepath 
        param:path 
        
        """
        args={}
        args["spacename"]=spacename
        args["spacepath"]=spacepath
        args["path"]=path
        return self._te["notifySpaceNewDir"].execute4method(args,params={},actor=self)
    

    def prepareActorSpecs(self,app,actor,**args):
        """
        compress specs for specific actor and targz in appropriate download location
        param:app name of app
        param:actor name of actor
        result bool 
        
        """
        result=None

        actorname= actor
        appname= app

        filesroot=o.core.portal.runningPortal.filesroot

        actorloader=o.core.portal.runningPortal.actorsloader.id2object["%s__%s" % (appname,actorname)]

        path=o.system.fs.joinPaths(actorloader.model.path,"specs")

        pathdest=o.system.fs.joinPaths(filesroot,"specs","%s_%s.tgz"%(appname,actorname))
        o.system.fs.remove(pathdest)
        #o.system.fs.createDir(o.system.fs.joinPaths("files","specs"))

        if not o.system.fs.exists(path):
            return {"error":"could not find spec path for app %s actor %s" % (appname,actorname)}
        else:
            o.system.fs.targzCompress(path,pathdest)

        return result
    

    def wikisave(self,authkey,text,**args):
        """
        param:authkey key to authenticate doc
        param:text content of file to edit
        result bool 
        
        """
        contents = o.apps.system.contentmanager.dbmem.cacheGet(authkey)
        o.system.fs.writeFile(contents['path'],text)
        o.core.portal.runningPortal.webserver.loadSpace(contents['space'])
        returnpath = "/%s/%s" % (contents['space'], contents['page'])
        returncontent = "<script>window.open('%s', '_self', '');</script>" % returnpath

        return returncontent
    
