from OpenWizzy import o
from LoaderBase import LoaderBase, LoaderBaseObject

from OpenWizzy.core.extensions.PMExtensionsGroup import PMExtensionsGroup
from OpenWizzy.core.extensions.PMExtensions import PMExtensions
import OpenWizzy.baselib.tags

class ActorExtensionsGroup(PMExtensionsGroup):
    """
    ActorExtensionsGroup
    """

    def __init__(self, path):
        """
        ActorExtensionsGroup constructor
        """

        PMExtensionsGroup.__init__(self)

        self.pm_name = "a"
        self.pm_location = "a"

        extensionLoader = PMExtensions(self, 'a.')

        extensionLoader.load(path,True)

        self._activate()


    def _activate(self):
        """
        Activates all extensions in the extention group
        """
        for extensionName in self.pm_extensions.keys():
            extension = self.pm_extensions[extensionName]
            extension.activate()

class Class():
    pass

class ActorLoader(LoaderBaseObject):
    def __init__(self):
        LoaderBaseObject.__init__(self,"actor")

    def createDefaults(self,path):
        self._createDefaults(path,["users.cfg"])
        base=o.system.fs.joinPaths(o.core.portalloader.getTemplatesPath(),".%s"%self.type,"dirstructure")
        o.system.fs.copyDirTree(base,path,overwriteFiles=False)

    def raiseError(self,msg,path=None):
        #if path==None:
        #    path=self.model.path
        #o.system.fs.writeFile(o.system.fs.joinPaths(path,"ERROR.TXT"),msg)
        #@todo kristof use proper event mgmt 
        return False

    def loadFromDisk(self,path,reset=False):
        #the name is $appname__actorname all in lowercase
        name=o.system.fs.getDirName(path,True)
        if name.find("__")<>-1:
            app,actor=name.split("__",1)
        else:
            return self.raiseError("Cannot create actor, name of directory needs to be $appname__$actorname",path=path)
        self._loadFromDisk(path,reset=False)
        self.model.application=app
        self.model.actor=actor
        self.save()

    def _removeFromMem(self):
        print "remove actor %s from memory" % self.model.id
        o.core.specparser.removeSpecsForActor(self.model.application,self.model.actor)
        o.core.codegenerator.removeFromMem(self.model.application,self.model.actor)
        o.core.portal.runningPortal.webserver.unloadActorFromRoutes(self.model.application,self.model.actor)
        key="%s_%s" % (self.model.application.lower(),self.model.actor.lower())
        if o.core.portal.runningPortal.actors.has_key(key):
            o.core.portal.runningPortal.actors.pop(key)

    def reset(self):
        self._removeFromMem()
        self.loadFromDisk(self.model.path,reset=True)        
        o.core.portal.runningPortal.actorsloader.getActor(self.model.application,self.model.actor)

    def activate(self):
        print "activate actor: %s %s" % (self.model.application,self.model.actor)
        result= o.apps.actorsloader._generateLoadActor(self.model.application,self.model.actor,self.model.path)
        return result

    def loadSpace(self):
        #LOAD SPACES FOR ACTOR
        #check if we need to load space for actor
        sloader=o.core.portal.runningPortal.webserver.spacesloader

        
        key="space_%s__%s"%(self.model.application,self.model.actor)
        # if not sloader.spaces.has_key(key):
        ppath=o.system.fs.joinPaths(self.model.path,key)
        if True or not o.system.fs.exists(ppath): #@todo despiegk loader
            self.activate()  
        sloader.scan(ppath) 



class ActorsLoader(LoaderBase):
    def __init__(self):
        """
        """
        LoaderBase.__init__(self,"actor",ActorLoader)
        self.actorIdToActorLoader=self.id2object
        self.getActorLoaderFromId=self.getLoaderFromId
        self.osiscl = None

    def reset(self):
        o.apps=Class()
        o.apps.__dict__["actorsloader"]=self
        o.core.specparser.app_actornames={}
        o.core.specparser.actornames=[]
        o.core.specparser.appnames=[]
        o.core.specparser.modelnames={}
        o.core.specparser.roles={}
        o.core.specparser.specs={}
        o.core.codegenerator.classes={}
        #o.core.portal.runningPortal._init()

    def getApps(self):
        result={}
        for item in self.id2object.keys():
            if item.find("__")<>-1:
                app=item.split("__")[0]
                result[app]=1
        return result.keys()

    def getAppActors(self):
        result=[]
        for item in self.id2object.keys():
            if item.find("__")<>-1:
                app,actor=item.split("__",2)
                result.append([app,actor])
        return result


    def getActor(self,appname,actorname):

        key="%s__%s" % (appname.lower(),actorname.lower())

        if o.core.portal.runningPortal.actors.has_key(key):
            return o.core.portal.runningPortal.actors[key]

        print "get actor cache miss for %s %s"%(appname,actorname)

        if self.actorIdToActorLoader.has_key(key):
            loader=self.actorIdToActorLoader[key]
            aobj=loader.activate()
            o.core.portal.runningPortal.actors[key]=aobj
            return o.core.portal.runningPortal.actors[key]
        else:
            raise RuntimeError("Cannot find actor from app %s with name %s"%(appname,actorname))

    def existsActorLoader(self,appname,actorname):
        key="%s__%s" % (appname.lower(),actorname.lower())
        return self.id2object.has_key(key)

    def existsActor(self,appname,actorname):
        key="%s__%s" % (appname.lower(),actorname.lower())
        return o.core.portal.runningPortal.actors.has_key(key)

    def _descrTo1Line(self,descr):        
        if descr=="":
            return descr
        descr=descr.strip()
        descr=descr.replace("\n","\\n")
        #descr=descr.replace("'n","")
        return descr

    def loadOsisTasklets(self,actorobject,actorpath,modelname):
        path=o.system.fs.joinPaths(actorpath,"osis",modelname)
        if o.system.fs.exists(path):
            for method in ["set","get","delete","list","find","datatables"]:
                path2=o.system.fs.joinPaths(path,"method_%s"%method)
                actorobject._te["model_%s_%s"%(modelname,method)]=o.core.taskletengine.get(path2)


    def _generateLoadActor(self,appname,actorname,actorpath):
        #parse the specs
        o.core.specparser.parseSpecs("%s/specs"%actorpath,appname=appname,actorname=actorname)

        #retrieve the just parsed spec
        spec=o.core.specparser.getActorSpec(appname,actorname,raiseError=False)
        if spec==None:
            return None

        if spec.tags==None:
            spec.tags=""
        tags=o.core.tags.getObject(spec.tags)

        spec.hasTasklets=tags.labelExists("tasklets")

        #generate the tasklets for the methods of the actor
        # o.core.codegenerator.generate(spec,"tasklet",codepath=actorpath)

        #generate the class for the methods of the actor
        args={}
        args["tags"]=tags
        classpath=o.system.fs.joinPaths(actorpath,"methodclass","%s_%s.py"%(spec.appname,spec.actorname))
        modelNames = o.core.specparser.getModelNames(appname, actorname)
        actorobject =o.core.codegenerator.generate(spec,"actorclass",codepath=actorpath,classpath=classpath,\
            args=args,makeCopy=True)()


        #create spacedir if needed
        #create space for actor if it does not exist yet
        ppathx=o.system.fs.joinPaths(actorpath,"space_%s__%s"%(appname,actorname))
        if not o.system.fs.exists(ppathx):
            o.system.fs.createDir(ppathx)
            ppath2=o.system.fs.joinPaths(ppathx,".space")
            o.system.fs.createDir(ppath2)
            ppath2=o.system.fs.joinPaths(ppathx,".macros")
            o.system.fs.createDir(ppath2)            
            ppath2=o.system.fs.joinPaths(ppathx,"space_%s.wiki"%actorname) 
            C="""
h3. home page for space $$space

...

"""
            o.system.fs.writeFile(ppath2,C)

        
        if len(modelNames)>0:
            actorobject.models=Class()

            for modelName in modelNames:
                modelspec=o.core.specparser.getModelSpec(appname,actorname,modelName)
                modeltags=o.core.tags.getObject(modelspec.tags)


                #will generate the tasklets
                modelHasTasklets=modeltags.labelExists("tasklets")
                if modelHasTasklets:
                    o.core.codegenerator.generate(modelspec,"osis",codepath=actorpath,returnClass=False,args=args)

                if spec.hasTasklets:
                    self.loadOsisTasklets(actorobject,actorpath,modelname=modelspec.name)

                classs=o.core.codegenerator.getClassPymodel(appname,actorname,modelName,codepath=actorpath)
                if modelspec.tags==None:
                    modelspec.tags=""
                index=o.core.tags.getObject(modelspec.tags).labelExists("index")
                tags=o.core.tags.getObject(modelspec.tags)

                db = o.db.keyvaluestore.getMemoryStore()
                osis = False
                if tags.tagExists("dbtype"):
                    dbtypes=[item.lower() for item in tags.tagGet("dbtype").split(",")]
                    if "arakoon" in dbtypes:
                        if dbtypes.index("arakoon")==0:
                            db = o.db.keyvaluestore.getArakoonStore(modelName) 
                    if "fs" in dbtypes:
                        if dbtypes.index("fs")==0:
                            db = o.db.keyvaluestore.getFileSystemStore(namespace=modelName, serializers=[o.db.serializers.getSerializerType('j')])
                    if "redis" in dbtypes:
                        if dbtypes.index("redis")==0:
                            db = o.db.keyvaluestore.getRedisStore(namespace=modelName, serializers=[o.db.serializers.getSerializerType('j')])
                    if "osis" in dbtypes:
                        osis = True
                    
                if osis:
                    #We need to check if the correct namespace is existing and
                    #the namespace maps to the actor name, every object is a
                    #category
                    namespacename = actorname
                    if not self.osiscl:
                        import OpenWizzy.grid.osis
                        self.osiscl = o.core.osis.getClient()
                    if actorname not in self.osiscl.listNamespaces():
                        template = tags.tagGet('osis_template', 'modelobjects')
                        self.osiscl.createNamespace(actorname, template=template)
                    if modelName not in self.osiscl.listNamespaceCategories(namespacename):
                        self.osiscl.createNamespaceCategory(namespacename, modelName)
                try:
                    if not osis:
                        actorobject.models.__dict__[modelName]=o.core.osismodel.get(appname,actorname,modelName,classs,db,index)
                    else:
                        actorobject.models.__dict__[modelName]  = o.core.osismodel.getRemoteOsisDB(appname, actorname, modelName, classs)
                except Exception,e:
                    raise
                    msg="Could not get osis model for %s_%s_%s.Error was %s."%(appname,actorname,modelName,e)
                    raise RuntimeError(msg)
        #add routes to webserver
        for methodspec in spec.methods:
            #make sure tasklets are loaded

            methodtags=o.core.tags.getObject(methodspec.tags)
            methodspec.hasTasklets=methodtags.labelExists("tasklets")

            if methodspec.hasTasklets or spec.hasTasklets:
                taskletpath=o.system.fs.joinPaths(actorpath,"methodtasklets","method_%s" %methodspec.name)
                if not o.system.fs.exists(taskletpath):
                    o.system.fs.createDir(taskletpath)
                    taskletContent = """
def main(o, args, params, actor, tags, tasklet):
    return params

def match(o, args, params, actor, tags, tasklet):
    return True
                    """
                    methodtasklet = o.system.fs.joinPaths(taskletpath, "5_%s.py" % methodspec.name)
                    o.system.fs.writeFile(methodtasklet, taskletContent)
                actorobject._te[methodspec.name]=o.core.taskletengine.get(taskletpath)

            if o.core.portal.__dict__.has_key("runningPortal"):

                paramvalidation={}
                for var in methodspec.vars:
                    paramvalidation[var.name]=""  #@todo

                paramoptional={}
                for var in methodspec.vars:
                    tags=o.core.tags.getObject(var.tags)
                    if tags.labelExists("optional"):
                        paramoptional[var.name]=""

                paramdescription={}
                for var in methodspec.vars:
                    tags=o.core.tags.getObject(var.tags)
                    if tags.labelExists("optional"):
                        descr=var.description+" (optional)"
                    else:
                        descr=var.description
                    paramdescription[var.name]=self._descrTo1Line(descr)

                tags=o.core.tags.getObject(methodspec.tags)    
                if tags.tagExists("returnformat"):
                    returnformat= tags.tagGet("returnformat")
                else:
                    returnformat=None
                
                auth=not tags.labelExists("noauth")
                methodcall = getattr(actorobject, methodspec.name)
                o.core.portal.runningPortal.webserver.addRoute(methodcall,appname,actorname,methodspec.name,\
                    paramvalidation=paramvalidation,paramdescription=paramdescription,paramoptional=paramoptional,\
                    description=methodspec.description,auth=auth,returnformat=returnformat)
                actorobjects = modelNames
                o.core.portal.runningPortal.webserver.addExtRoute(methodcall,appname,actorname,methodspec.name,
                        actorobjects,
                        paramvalidation=paramvalidation,paramdescription=paramdescription,paramoptional=paramoptional,description=methodspec.description,auth=auth,returnformat=returnformat)







        #load taskletengines if they do exist
        tepath=o.system.fs.joinPaths(actorpath,"taskletengines")
        if o.system.fs.exists(tepath):
            if not actorobject.__dict__.has_key("taskletengines"):
                actorobject.taskletengines=Class()
            tepaths=o.system.fs.listDirsInDir(tepath)
            for tepath in tepaths:
                actorobject.taskletengines.__dict__[o.system.fs.getBaseName(tepath)]=o.core.taskletengine.get(tepath)

        
        #LOAD actorobject to qbase tree
        if not o.apps.__dict__.has_key(appname):
            o.apps.__dict__[appname]=Class()

        if not o.apps.__dict__[appname].__dict__.has_key(actorname):
            o.apps.__dict__[appname].__dict__[actorname]=actorobject

        if o.core.portal.__dict__.has_key("runningAppserver"):
            key="%s_%s" % (spec.appname.lower(),spec.actorname.lower())
            o.core.portal.runningPortal.actors[key]=actorobject

        #load extensions
        actorobject.__dict__['extensions'] = ActorExtensionsGroup(o.system.fs.joinPaths(actorpath,"extensions"))

        #load macros
        macropath=o.system.fs.joinPaths(actorpath,"macros")
        if o.system.fs.exists(macropath):
            macropath2=o.system.fs.joinPaths(macropath,"preprocess")
            o.core.portal.runningPortal.webserver.macroexecutorPreprocessor.taskletsgroup.addTasklets(macropath2)
            macropath2=o.system.fs.joinPaths(macropath,"page")
            o.core.portal.runningPortal.webserver.macroexecutorPage.taskletsgroup.addTasklets(macropath2)
            macropath2=o.system.fs.joinPaths(macropath,"wiki")
            o.core.portal.runningPortal.webserver.macroexecutorWiki.taskletsgroup.addTasklets(macropath2)

        return actorobject



