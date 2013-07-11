from pylabs import q
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
        return q.core.appserver6.runningAppserver.webserver.actorsloader._objects.keys()    

    def getActorsWithPaths(self,**args):
        """
        result list([name,path]) 
        
        """
        actors=[]
        for actor in q.core.appserver6.runningAppserver.actorsloader.id2object.keys():
            actor=q.core.appserver6.runningAppserver.actorsloader.id2object[actor]
            actors.append([actor.model.id,actor.model.path])
        return actors
    

    def getBuckets(self,**args):
        """
        result list(str) 
        
        """
        return q.core.appserver6.runningAppserver.webserver.bucketsloader._objects.keys()

    def getBucketsWithPaths(self,**args):
        """
        result list([name,path]) 
        
        """
        buckets=[]
        for bucket in q.core.appserver6.runningAppserver.webserver.bucketsloader.id2object.keys():
            bucket=q.core.appserver6.runningAppserver.webserver.bucketsloader.id2object[bucket]
            buckets.append([bucket.model.id,bucket.model.path])
        return buckets

    def getContentDirsWithPaths(self,**args):
        """
        return root dirs of content (actors,buckets,spaces)
        result list([name,path]) 
        
        """
        objects=[]
        for objectname in q.core.appserver6.runningAppserver.webserver.contentdirs.keys():
            objectpath=q.core.appserver6.runningAppserver.webserver.contentdirs[objectname]
            objects.append([objectname,objectpath])
        return objects
    

    def getSpaces(self,**args):
        """
        result list(str) 
        
        """
        return q.core.appserver6.runningAppserver.webserver.spacesloader.spaces.keys()
    

    def getSpacesWithPaths(self,**args):
        """
        result list([name,path]) 
        
        """
        spaces=[]
        for space in q.core.appserver6.runningAppserver.webserver.spacesloader.spaces.keys():
            space=q.core.appserver6.runningAppserver.webserver.spacesloader.spaces[space]
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
        actor=q.core.appserver6.runningAppserver.actorsloader.getActor(appname,actorname)     
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
            q.core.appserver6.runningAppserver.webserver.loadSpace(spacename)
        else:
            q.core.appserver6.runningAppserver.webserver.loadSpace(self.appname)
        return []

    def reloadAll(self,id):
        def reloadApp():
            print "RELOAD APP FOR ACTORS Delete"
            q.core.appserver6.runningAppserver.reset()

        q.core.appserver6.runningAppserver.actorsloader.id2object.pop(id)

        q.core.appserver6.runningAppserver.scheduler.scheduleFromNow(2,9,reloadApp)
        q.core.appserver6.runningAppserver.scheduler.scheduleFromNow(10,9,reloadApp)
    

    def notifyActorModification(self,id,**args):
        """
        param:id id of actor which changed
        result bool 
        
        """
        loaders=q.core.appserver6.runningAppserver.actorsloader
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

        if not q.core.appserver6.runningAppserver.actorsloader.actors.has_key(key):
            #actor does not exist yet, create required dirs in basedir
            if path=="":
                path=q.system.fs.joinPaths(q.core.appserver6.runningAppserver.webserver.basepath,"actors",key)
                q.system.fs.createDir(path)
                q.system.fs.createDir(q.system.fs.joinPaths(path,".actor"))
            else:
                q.system.fs.createDir(path)
                q.system.fs.createDir(q.system.fs.joinPaths(path,".actor"))
                
            print "scan path:%s"%path
            q.core.appserver6.runningAppserver.actorsloader.scan(path)
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
        loaders=q.core.appserver6.runningAppserver.webserver.bucketsloader
        loaders.removeLoader(id)
        
        def reloadApp(id=None):        
            q.core.appserver6.runningAppserver.webserver.loadSpaces(reset=True)

        #loader.pop(id)
        # q.core.appserver6.runningAppserver.scheduler.scheduleFromNow(1,9,reloadApp,id=id)
        q.core.appserver6.runningAppserver.scheduler.scheduleFromNow(10,9,reloadApp,id=id)
        return result
        

    def notifyBucketModification(self,id,**args):
        """
        param:id id of bucket which changed
        result bool 
        
        """
        loaders=q.core.appserver6.runningAppserver.webserver.bucketsloader
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

        loader=q.core.appserver6.runningAppserver.webserver.bucketsloader

        if not loader.id2object.has_key(key):
            #does not exist yet, create required dirs in basedir
            if path=="":
                path=q.system.fs.joinPaths(q.core.appserver6.runningAppserver.webserver.basepath,"buckets",key)
                q.system.fs.createDir(path)
                q.system.fs.createDir(q.system.fs.joinPaths(path,".bucket"))
            else:
                q.system.fs.createDir(path)
                q.system.fs.createDir(q.system.fs.joinPaths(path,".bucket"))
                
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
        loaders=q.core.appserver6.runningAppserver.webserver.spacesloader
        loaders.removeLoader(id)
        
        def reloadApp():
            print "RELOAD APP SPACE DELETE"
            q.core.appserver6.runningAppserver.webserver.loadSpaces(reset=True)

        # loader=q.core.appserver6.runningAppserver.webserver.spacesloader.id2object
        # loader.pop(id)

        q.core.appserver6.runningAppserver.scheduler.scheduleFromNow(10,9,reloadApp)

    

    def notifySpaceModification(self,id,**args):
        """
        param:id id of space which changed
        result bool 
        
        """

        loaders=q.core.appserver6.runningAppserver.webserver.spacesloader
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

        loader=q.core.appserver6.runningAppserver.webserver.spacesloader

        if not loader.id2object.has_key(key):
            #does not exist yet, create required dirs in basedir
            if path=="":
                path=q.system.fs.joinPaths(q.core.appserver6.runningAppserver.webserver.basepath,"spaces",name)            
            else:
                q.system.fs.createDir(path)
                
            #create default content
            mddir=q.system.fs.joinPaths(path,".space")
            dest=q.system.fs.joinPaths(path,"%s.wiki"%name)
            q.system.fs.createDir(mddir)                
            loader.scan(path)
            source=q.system.fs.joinPaths(mddir,"template.wiki")
            q.system.fs.copyFile(source,dest)
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

        filesroot=q.core.appserver6.runningAppserver.filesroot

        actorloader=q.core.appserver6.runningAppserver.actorsloader.id2object["%s__%s" % (appname,actorname)]

        path=q.system.fs.joinPaths(actorloader.model.path,"specs")

        pathdest=q.system.fs.joinPaths(filesroot,"specs","%s_%s.tgz"%(appname,actorname))
        q.system.fs.remove(pathdest)
        #q.system.fs.createDir(q.system.fs.joinPaths("files","specs"))

        if not q.system.fs.exists(path):
            return {"error":"could not find spec path for app %s actor %s" % (appname,actorname)}
        else:
            q.system.fs.targzCompress(path,pathdest)

        return result
    

    def wikisave(self,authkey,text,**args):
        """
        param:authkey key to authenticate doc
        param:text content of file to edit
        result bool 
        
        """
        contents = q.apps.system.contentmanager.dbmem.cacheGet(authkey)
        q.system.fs.writeFile(contents['path'],text)
        q.core.appserver6.runningAppserver.webserver.loadSpace(contents['space'])
        returnpath = "/%s/%s" % (contents['space'], contents['page'])
        returncontent = "<script>window.open('%s', '_self', '');</script>" % returnpath

        return returncontent
    
