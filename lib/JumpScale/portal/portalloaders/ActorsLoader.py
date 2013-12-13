from JumpScale import j
from LoaderBase import LoaderBase, LoaderBaseObject

from JumpScale.core.extensions.PMExtensionsGroup import PMExtensionsGroup
from JumpScale.core.extensions.PMExtensions import PMExtensions
import JumpScale.baselib.tags


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

        extensionLoader.load(path, True)

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
        LoaderBaseObject.__init__(self, "actor")

    def createDefaults(self, path):
        self._createDefaults(path, ["users.cfg"])
        base = j.system.fs.joinPaths(j.core.portalloader.getTemplatesPath(), ".%s" % self.type, "dirstructure")
        j.system.fs.copyDirTree(base, path, overwriteFiles=False)

    def raiseError(self, msg, path=None):
        # if path==None:
        #    path=self.model.path
        # j.system.fs.writeFile(j.system.fs.joinPaths(path,"ERROR.TXT"),msg)
        #@todo kristof use proper event mgmt
        return False

    def loadFromDisk(self, path, reset=False):
        # the name is $appname__actorname all in lowercase
        name = j.system.fs.getDirName(path, True)
        if name.find("__") != -1:
            app, actor = name.split("__", 1)
        else:
            return self.raiseError("Cannot create actor, name of directory needs to be $appname__$actorname", path=path)
        self._loadFromDisk(path, reset=False)
        self.model.application = app
        self.model.actor = actor
        self.save()

    def _removeFromMem(self):
        print "remove actor %s from memory" % self.model.id
        j.core.specparser.removeSpecsForActor(self.model.application, self.model.actor)
        j.core.codegenerator.removeFromMem(self.model.application, self.model.actor)
        j.core.portal.runningPortal.webserver.unloadActorFromRoutes(self.model.application, self.model.actor)
        key = "%s_%s" % (self.model.application.lower(), self.model.actor.lower())
        if key in j.core.portal.runningPortal.actors:
            j.core.portal.runningPortal.actors.pop(key)

    def reset(self):
        self._removeFromMem()
        self.loadFromDisk(self.model.path, reset=True)
        j.core.portal.runningPortal.actorsloader.getActor(self.model.application, self.model.actor)

    def activate(self):
        print "activate actor: %s %s" % (self.model.application, self.model.actor)
        result = j.apps.actorsloader._generateLoadActor(self.model.application, self.model.actor, self.model.path)
        return result

    def loadSpace(self):
        # LOAD SPACES FOR ACTOR
        # check if we need to load space for actor
        sloader = j.core.portal.runningPortal.webserver.spacesloader

        key = "space_%s__%s" % (self.model.application, self.model.actor)
        # if not sloader.spaces.has_key(key):
        ppath = j.system.fs.joinPaths(self.model.path, key)
        if True or not j.system.fs.exists(ppath):  # @todo despiegk loader
            self.activate()
        sloader.scan(ppath)


class ActorsLoader(LoaderBase):

    def __init__(self):
        """
        """
        LoaderBase.__init__(self, "actor", ActorLoader)
        self.actorIdToActorLoader = self.id2object
        self.getActorLoaderFromId = self.getLoaderFromId
        self.osiscl = None

    def reset(self):
        j.apps = Class()
        j.apps.__dict__["actorsloader"] = self
        j.core.specparser.app_actornames = {}
        j.core.specparser.actornames = []
        j.core.specparser.appnames = []
        j.core.specparser.modelnames = {}
        j.core.specparser.roles = {}
        j.core.specparser.specs = {}
        j.core.codegenerator.classes = {}
        # j.core.portal.runningPortal._init()

    def getApps(self):
        result = {}
        for item in self.id2object.keys():
            if item.find("__") != -1:
                app = item.split("__")[0]
                result[app] = 1
        return result.keys()

    def getAppActors(self):
        result = []
        for item in self.id2object.keys():
            if item.find("__") != -1:
                app, actor = item.split("__", 2)
                result.append([app, actor])
        return result

    def getActor(self, appname, actorname):

        key = "%s__%s" % (appname.lower(), actorname.lower())

        if key in j.core.portal.runningPortal.actors:
            return j.core.portal.runningPortal.actors[key]

        print "get actor cache miss for %s %s" % (appname, actorname)

        if key in self.actorIdToActorLoader:
            loader = self.actorIdToActorLoader[key]
            aobj = loader.activate()
            j.core.portal.runningPortal.actors[key] = aobj
            return j.core.portal.runningPortal.actors[key]
        else:
            raise RuntimeError("Cannot find actor from app %s with name %s" % (appname, actorname))

    def existsActorLoader(self, appname, actorname):
        key = "%s__%s" % (appname.lower(), actorname.lower())
        return key in self.id2object

    def existsActor(self, appname, actorname):
        key = "%s__%s" % (appname.lower(), actorname.lower())
        return key in j.core.portal.runningPortal.actors

    def _descrTo1Line(self, descr):
        if descr == "":
            return descr
        descr = descr.strip()
        descr = descr.replace("\n", "\\n")
        # descr=descr.replace("'n","")
        return descr

    def loadOsisTasklets(self, actorobject, actorpath, modelname):
        path = j.system.fs.joinPaths(actorpath, "osis", modelname)
        if j.system.fs.exists(path):
            for method in ["set", "get", "delete", "list", "find", "datatables"]:
                path2 = j.system.fs.joinPaths(path, "method_%s" % method)
                actorobject._te["model_%s_%s" % (modelname, method)] = j.core.taskletengine.get(path2)

    def _generateLoadActor(self, appname, actorname, actorpath):
        # parse the specs
        j.core.specparser.parseSpecs("%s/specs" % actorpath, appname=appname, actorname=actorname)

        # retrieve the just parsed spec
        spec = j.core.specparser.getActorSpec(appname, actorname, raiseError=False)
        if spec == None:
            return None

        if spec.tags == None:
            spec.tags = ""
        tags = j.core.tags.getObject(spec.tags)

        spec.hasTasklets = tags.labelExists("tasklets")

        # generate the tasklets for the methods of the actor
        # j.core.codegenerator.generate(spec,"tasklet",codepath=actorpath)

        # generate the class for the methods of the actor
        args = {}
        args["tags"] = tags
        classpath = j.system.fs.joinPaths(actorpath, "methodclass", "%s_%s.py" % (spec.appname, spec.actorname))
        modelNames = j.core.specparser.getModelNames(appname, actorname)
        
        actorobject = j.core.codegenerator.generate(spec, "actorclass", codepath=actorpath, classpath=classpath,
                                                    args=args, makeCopy=True)()             

        # # create spacedir if needed
        # # create space for actor if it does not exist yet
        # ppathx = j.system.fs.joinPaths(actorpath, "space_%s__%s" % (appname, actorname))
        # if not j.system.fs.exists(ppathx):
        #     j.system.fs.createDir(ppathx)
        #     ppath2 = j.system.fs.joinPaths(ppathx, ".space")
        #     j.system.fs.createDir(ppath2)
        #     ppath2 = j.system.fs.joinPaths(ppathx, ".macros")
        #     j.system.fs.createDir(ppath2)
#             ppath2 = j.system.fs.joinPaths(ppathx, "space_%s.wiki" % actorname)
#             C = """
# h3. home page for space $$space

# ...

# """
#             j.system.fs.writeFile(ppath2, C)

        if len(modelNames) > 0:
            actorobject.models = Class()

            for modelName in modelNames:
                modelspec = j.core.specparser.getModelSpec(appname, actorname, modelName)
                modeltags = j.core.tags.getObject(modelspec.tags)

                # will generate the tasklets
                modelHasTasklets = modeltags.labelExists("tasklets")
                if modelHasTasklets:
                    j.core.codegenerator.generate(modelspec, "osis", codepath=actorpath, returnClass=False, args=args)

                if spec.hasTasklets:
                    self.loadOsisTasklets(actorobject, actorpath, modelname=modelspec.name)

                classs = j.core.codegenerator.getClassPymodel(appname, actorname, modelName, codepath=actorpath)
                if modelspec.tags == None:
                    modelspec.tags = ""
                index = j.core.tags.getObject(modelspec.tags).labelExists("index")
                tags = j.core.tags.getObject(modelspec.tags)

                db = j.db.keyvaluestore.getMemoryStore()
                osis = False
                if tags.tagExists("dbtype"):
                    dbtypes = [item.lower() for item in tags.tagGet("dbtype").split(",")]
                    if "arakoon" in dbtypes:
                        if dbtypes.index("arakoon") == 0:
                            db = j.db.keyvaluestore.getArakoonStore(modelName)
                    if "fs" in dbtypes:
                        if dbtypes.index("fs") == 0:
                            db = j.db.keyvaluestore.getFileSystemStore(namespace=modelName, serializers=[j.db.serializers.getSerializerType('j')])
                    if "redis" in dbtypes:
                        if dbtypes.index("redis") == 0:
                            db = j.db.keyvaluestore.getRedisStore(namespace=modelName, serializers=[j.db.serializers.getSerializerType('j')])
                    if "osis" in dbtypes:
                        osis = True

                if osis:
                    # We need to check if the correct namespace is existing and
                    # the namespace maps to the actor name, every object is a
                    # category
                    namespacename = actorname
                    if not self.osiscl:
                        import JumpScale.grid.osis
                        self.osiscl = j.core.osis.getClient()
                    if actorname not in self.osiscl.listNamespaces():
                        template = tags.tagGet('osis_template', 'modelobjects')
                        self.osiscl.createNamespace(actorname, template=template)
                    if modelName not in self.osiscl.listNamespaceCategories(namespacename):
                        self.osiscl.createNamespaceCategory(namespacename, modelName)
                try:
                    if not osis:
                        actorobject.models.__dict__[modelName] = j.core.osismodel.get(appname, actorname, modelName, classs, db, index)
                    else:
                        actorobject.models.__dict__[modelName] = j.core.osismodel.getRemoteOsisDB(appname, actorname, modelName, classs)
                except Exception as e:
                    raise
                    msg = "Could not get osis model for %s_%s_%s.Error was %s." % (appname, actorname, modelName, e)
                    raise RuntimeError(msg)
        # add routes to webserver
        for methodspec in spec.methods:
            # make sure tasklets are loaded

            methodtags = j.core.tags.getObject(methodspec.tags)
            methodspec.hasTasklets = methodtags.labelExists("tasklets")

            if methodspec.hasTasklets or spec.hasTasklets:
                taskletpath = j.system.fs.joinPaths(actorpath, "methodtasklets", "method_%s" % methodspec.name)
                if not j.system.fs.exists(taskletpath):
                    j.system.fs.createDir(taskletpath)
                    taskletContent = """
def main(j, args, params, actor, tags, tasklet):
    return params

def match(j, args, params, actor, tags, tasklet):
    return True
                    """
                    methodtasklet = j.system.fs.joinPaths(taskletpath, "5_%s.py" % methodspec.name)
                    j.system.fs.writeFile(methodtasklet, taskletContent)
                actorobject._te[methodspec.name] = j.core.taskletengine.get(taskletpath)

            if "runningPortal" in j.core.portal.__dict__:

                paramvalidation = {}
                for var in methodspec.vars:
                    paramvalidation[var.name] = ""  # @todo

                paramoptional = {}
                for var in methodspec.vars:
                    tags = j.core.tags.getObject(var.tags)
                    if tags.labelExists("optional"):
                        paramoptional[var.name] = ""

                paramdescription = {}
                for var in methodspec.vars:
                    tags = j.core.tags.getObject(var.tags)
                    if tags.labelExists("optional"):
                        descr = var.description + " (optional)"
                    else:
                        descr = var.description
                    paramdescription[var.name] = self._descrTo1Line(descr)

                tags = j.core.tags.getObject(methodspec.tags)
                if tags.tagExists("returnformat"):
                    returnformat = tags.tagGet("returnformat")
                else:
                    returnformat = None

                auth = not tags.labelExists("noauth")
                methodcall = getattr(actorobject, methodspec.name)
                j.core.portal.runningPortal.webserver.addRoute(methodcall, appname, actorname, methodspec.name,
                                                               paramvalidation=paramvalidation, paramdescription=paramdescription, paramoptional=paramoptional,
                                                               description=methodspec.description, auth=auth, returnformat=returnformat)
                actorobjects = modelNames
                j.core.portal.runningPortal.webserver.addExtRoute(methodcall, appname, actorname, methodspec.name,
                                                                  actorobjects,
                                                                  paramvalidation=paramvalidation, paramdescription=paramdescription, paramoptional=paramoptional, description=methodspec.description, auth=auth, returnformat=returnformat)

        # load taskletengines if they do exist
        tepath = j.system.fs.joinPaths(actorpath, "taskletengines")
        if j.system.fs.exists(tepath):
            if "taskletengines" not in actorobject.__dict__:
                actorobject.taskletengines = Class()
            tepaths = j.system.fs.listDirsInDir(tepath)
            for tepath in tepaths:
                actorobject.taskletengines.__dict__[j.system.fs.getBaseName(tepath)] = j.core.taskletengine.get(tepath)

        # LOAD actorobject to qbase tree
        if appname not in j.apps.__dict__:
            j.apps.__dict__[appname] = Class()

        if actorname not in j.apps.__dict__[appname].__dict__:
            j.apps.__dict__[appname].__dict__[actorname] = actorobject

        if "runningAppserver" in j.core.portal.__dict__:
            key = "%s_%s" % (spec.appname.lower(), spec.actorname.lower())
            j.core.portal.runningPortal.actors[key] = actorobject

        # load extensions
        actorobject.__dict__['extensions'] = ActorExtensionsGroup(j.system.fs.joinPaths(actorpath, "extensions"))

        ##ACTOR DOES NOT NEED MACROS
        # # load macros
        # macropath = j.system.fs.joinPaths(actorpath, "macros")
        # if j.system.fs.exists(macropath):
        #     macropath2 = j.system.fs.joinPaths(macropath, "preprocess")
        #     j.core.portal.runningPortal.webserver.macroexecutorPreprocessor.taskletsgroup.addTasklets(macropath2)
        #     macropath2 = j.system.fs.joinPaths(macropath, "page")
        #     j.core.portal.runningPortal.webserver.macroexecutorPage.taskletsgroup.addTasklets(macropath2)
        #     macropath2 = j.system.fs.joinPaths(macropath, "wiki")
        #     j.core.portal.runningPortal.webserver.macroexecutorWiki.taskletsgroup.addTasklets(macropath2)

        return actorobject
