from JumpScale import j
import JumpScale.baselib.elasticsearch
import ujson

class OSISCMDS(object):

    def __init__(self, daemon):
        self.daemon = daemon
        self.osisInstances = {}  # key is namespace_categoryname
        self.db = None  # default db
        self.elasticsearch = None  # default elastic search connection
        self.path="%s/apps/osis/logic"%j.dirs.baseDir

    def authenticate(self, namespace, categoryname, name,passwd, session=None):
        """
        authenticates a user and returns the groups in which the user is
        """
        if namespace<>"system" and categoryname<>"user":
            raise RuntimeError("Cannot process, only supported for system/user namespace")
        oi = self._getOsisInstanceForCat("system", "user")

        key="%s_%s"%(j.application.whoAmI.gid,name)
        if not oi.exists(key):
            return {"authenticated":False,"exists":False}

        user=ujson.loads(oi.get(key))

        if user["passwd"]==j.tools.hash.md5_string(passwd) or user["passwd"]==passwd:
            return {"authenticated":True,"exists":True,"groups":user["groups"],\
                "passwdhash":user["passwd"],"authkey":user["authkey"]}

        return {"authenticated":False,"exists":True}

    def get(self, namespace, categoryname, key, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"get",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on get %s_%s for user %s"%(namespace,categoryname,session.user))
        return oi.get(key)

    def exists(self, namespace, categoryname, key, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"get",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on exists %s_%s for user %s"%(namespace,categoryname,session.user))
        return oi.exists(key)

    def existsIndex(self, namespace, categoryname, key, timeout=1,session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"get",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on exists %s_%s for user %s"%(namespace,categoryname,session.user))
        return oi.existsIndex(key,timeout=timeout)


    def set(self, namespace, categoryname, key=None, value=None, waitIndex=False,session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        # print "WAITINDEXCMDS:%s"%waitIndex
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"set",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on get %s_%s for user %s"%(namespace,categoryname,session.user))
        return oi.set(key=key, value=value,waitIndex=waitIndex)

    def delete(self, namespace, categoryname, key, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"delete",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on get %s_%s for user %s"%(namespace,categoryname,session.user))        
        return oi.delete(key=key)

    def search(self, namespace, categoryname, query, start=0, size=None, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"search",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on get %s_%s for user %s"%(namespace,categoryname,session.user))
              
        result = oi.find(query, start, size)
        return result

    def list(self, namespace, categoryname, prefix=None, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"list",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on get %s_%s for user %s"%(namespace,categoryname,session.user))        
        if prefix==None:
            return oi.list()
        return oi.list(prefix)

    def _rebuildindex(self, namespace, categoryname, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"rebuildindex",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on get %s_%s for user %s"%(namespace,categoryname,session.user))
        return oi.rebuildindex()

    def rebuildindex(self, namespace=None, categoryname=None, session=None):
        if not namespace and not categoryname:
            for ns in self.listNamespaces():
                for cat in self.listNamespaceCategories(ns):
                    try:
                        self._rebuildindex(ns, cat, session)
                    except Exception, e:
                        j.errorconditionhandler.raiseOperationalWarning("Did not rebuild index for category '%s' in namespace '%s'. Error was: %s" % (cat, ns, e))
        else:
            self._rebuildindex(namespace, categoryname, session)

    def export(self, namespace, categoryname, outputpath, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"export",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on get %s_%s for user %s"%(namespace,categoryname,session.user))
        return oi.export(outputpath)

    def importFromPath(self, namespace, categoryname, path, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"import",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on get %s_%s for user %s"%(namespace,categoryname,session.user))
        return oi.importFromPath(path)

    def echo(self, msg="", session=None):
        return msg

    #################################################3

    def _getOsisInstanceForCat(self, namespace, category):
        fullname = "%s_%s" % (namespace, category)
        if fullname in self.osisInstances:
            return self.osisInstances[fullname]
        
        j.errorconditionhandler.raiseBug(
            message="cannot find osis local instance for namespace:%s & category:%s" % (namespace, category), die=False, \
            category="osis.valueerror")

    def _authenticateAdmin(self,session=None,user=None,passwd=None):
        if session<>None:
            user=session.user
            passwd=session.passwd
        
        if user=="root":
            if j.core.osis.superadminpasswd=="":
                j.application.loadConfig()
                j.core.osis.superadminpasswd=j.application.config.get("grid.master.superadminpasswd")
                if j.core.osis.superadminpasswd=="":

                    raise RuntimeError("grid.master.superadminpasswd cannot be empty in hrd")

            if passwd==j.core.osis.superadminpasswd:
                return True
            if j.tools.hash.md5_string(passwd)==j.core.osis.superadminpasswd:
                return True
        else:
            raise RuntimeError("Could not authenticate for admin usage, user login was %s"%user)

    def createNamespace(self, name=None, incrementName=False, template=None,session=None):
        """
        @return True
        """
        if session<>None:
            self._authenticateAdmin(session)
        #deal with incrementName
        if name == None:
            name = str()
        if incrementName:
            name += str(self._incrementNamespaceId())

        if j.system.fs.exists(j.system.fs.joinPaths(self.path, name)):
            #check namespace exists, if yes just return True
            return True

        #namespace does not exist yet
        j.system.fs.createDir(j.system.fs.joinPaths(self.path, name))
        if template <> None:
            j.system.fs.copyDirTree(j.system.fs.joinPaths(self.path, "_%s" % template), \
                j.system.fs.joinPaths(self.path, name), overwriteFiles=False)

        path = j.system.fs.joinPaths(self.path, name)

        self._initDefaultContent( namespacename=name)
        self.init(path=self.path, namespacename=name, template=template)
        return True

    def getOsisObjectClassCodeOrSpec(self,namespace,categoryname,session=None):
        """
        @return (1,spec file for osis complex time)
        @return (2,content of model.py)
        @return (3,"")  #could not find
        """

        path=j.system.fs.joinPaths(self.path, namespace,categoryname,"model.py")
        osismodelpath=j.system.fs.joinPaths(self.path, namespace,categoryname,"%s_%s_osismodelbase.py"%(namespace,categoryname))
        if j.system.fs.exists(osismodelpath):
            osismodelpathSpec=j.system.fs.joinPaths(self.path, namespace,"model.spec")
            return 1,j.system.fs.fileGetContents(osismodelpathSpec)
        elif j.system.fs.exists(path):
            return 2,j.system.fs.fileGetContents(path)
        else:
            return 3,""

    def listNamespaces(self, prefix="",session=None):
        ddirs = j.system.fs.listDirsInDir(self.path, dirNameOnly=True)

        ddirs = [item for item in ddirs if  not item.find("_") == 0]

        if prefix != "":
            ddirs = [item for item in ddirs if item.find(prefix) == 0]

        return ddirs


    def listNamespaceCategories(self, namespacename,session=None):
        ddirs = j.system.fs.listDirsInDir(j.system.fs.joinPaths(self.path,
                                                                namespacename), dirNameOnly=True)
        return ddirs

    def deleteNamespaceCategory(self, namespacename, name,removecode=False,session=None):
        """
        """
        if session<>None:
            self._authenticateAdmin(session)
        namespacepath = j.system.fs.joinPaths(self.path, namespacename)
        if not j.system.fs.exists(path=namespacepath):
            raise RuntimeError("Could not find namespace with name:%s"%namespacename)
        if removecode:
            j.system.fs.removeDirTree(j.system.fs.joinPaths(namespacepath, name))
        key="%s_%s"%(namespacename,name)
        try:
            self.elasticsearch.delete_index(key)
        except:
            pass
        self.db.destroy(key)
        self.db.destroy(key+"_incr")

    def createNamespaceCategory(self, namespacename, name,session=None):
        """
        """
        if session<>None:
            self._authenticateAdmin(session)
        namespacepath = j.system.fs.joinPaths(self.path, namespacename)
        if not j.system.fs.exists(path=namespacepath):
            raise RuntimeError("Could not find namespace with name:%s"%namespacename)

        j.system.fs.createDir(j.system.fs.joinPaths(namespacepath, name))

        self.init(path=self.path, overwriteImplementation=False, namespacename=namespacename)

    def _initDefaultContent(self,  namespacename=None):
        path = self.path
        if namespacename == None:
            for namespacename in j.system.fs.listDirsInDir(path, dirNameOnly=True):
                self._initDefaultContent(namespacename=namespacename)
        else:
            templatespath = "_templates"
            if j.system.fs.exists(path=templatespath):
                
                # if j.system.fs.exists(path):
                templatespath_namespace = j.system.fs.joinPaths(templatespath, "namespace")
                templatespath_category = j.system.fs.joinPaths(templatespath, "category")
                namespacepath = j.system.fs.joinPaths(path, namespacename)
                j.system.fs.copyDirTree(templatespath_namespace, namespacepath, overwriteFiles=False)
                if namespacename[0] <> "_" and j.system.fs.exists(path=j.system.fs.joinPaths(namespacepath, ".parentInTemplate")):  
                    # check if parent is coming from template
                    j.system.fs.remove(j.system.fs.joinPaths(namespacepath, "OSIS_parent.py"))
                    j.system.fs.remove(j.system.fs.joinPaths(namespacepath, "OSIS_parent.pyc"))

                for catname in j.system.fs.listDirsInDir(namespacepath, dirNameOnly=True):
                    catpath = j.system.fs.joinPaths(namespacepath, catname)
                    j.system.fs.copyDirTree(templatespath_category, catpath, overwriteFiles=False)
                    # j.system.fs.copyDirTree(templatespath_osistasklets,catpath,overwriteFiles=overwriteTasklets)

    def init(self, path="",overwriteImplementation=False, namespacename=None, template=None,initES=True,session=None):
        
        if session<>None:
            self._authenticateAdmin(session)

        if initES:
            eip=j.application.config.get("osis.elasticsearch.ip")
            eport=j.application.config.get("osis.elasticsearch.port")
            self.elasticsearch = j.clients.elasticsearch.get(ip=eip, port=int(eport))
            if path <> "":
                self.path = path
            else:
                path=self.path
            j.logger.consoleloglevel = 7
            # enable db's
            if j.application.config.get("osis.db.type") == "filesystem":
                self.db = j.db.keyvaluestore.getFileSystemStore("osis")
            else:
                raise RuntimeError("Only filesystem db implemented in osis")
            # wait for elastic search & get
            j.core.osis.db = self.db
            j.core.osis.elasticsearch = self.elasticsearch

        if namespacename == None:
            for namespacename in j.system.fs.listDirsInDir(path, dirNameOnly=True):
                self.init(path, overwriteImplementation=overwriteImplementation, namespacename=namespacename,initES=False)
        else:
            # te=j.core.taskletengine.get(j.system.fs.joinPaths("systemtasklets","init"))
            # te.executeV2(osis=self) #will add db & elasticsearch w
            if namespacename[0] == "_":
                return

            self._initDefaultContent(namespacename=namespacename)

            namespacepath = j.system.fs.joinPaths(path, namespacename)
            specpath=j.system.fs.joinPaths(path, namespacename, "model.spec")

            j.core.osis.generateOsisModelDefaults(namespacename,specpath)


            for catname in j.system.fs.listDirsInDir(namespacepath, dirNameOnly=True):
                catpath = j.system.fs.joinPaths(namespacepath, catname)


                #generate model class
                modelfile = j.system.fs.joinPaths(catpath, "model.py")
                if overwriteImplementation or not j.system.fs.exists(path=modelfile):
                    fileFrom = j.system.fs.joinPaths(namespacepath, "model_template.py")
                    if not j.system.fs.exists(fileFrom):
                        fileFrom = j.core.osis.getModelTemplate()
                    j.system.fs.copyFile(fileFrom, modelfile)
                    ed=j.codetools.getTextFileEditor(modelfile)
                    ed.replaceNonRegex("$categoryname",catname.capitalize())
                    ed.save()


                j.core.osis.getOsisModelClass(namespacename,catname)

                # check if there is already an implfile
                implfile = "OSIS_%s_impl.py" % catname
                implpath = j.system.fs.joinPaths(catpath, implfile)
                fileFrom = j.system.fs.joinPaths(namespacepath, "OSIS_category_template.py")
                if overwriteImplementation or not j.system.fs.exists(path=implpath):
                    j.system.fs.copyFile(fileFrom, implpath)

                ed=j.codetools.getTextFileEditor(implpath)
                ed.replaceNonRegex("$namespace",namespacename)
                ed.save()


                classs = j.core.osis._loadModuleClass(implpath)
                                          
                if namespacename[0] <> "_":
                    osis = classs()
                    osis.init(catpath,namespace=namespacename, categoryname=catname)
                    key = "%s_%s" % (namespacename, catname)
                    self.osisInstances[key] = osis



            # j.core.osis.db = None
            # j.core.osis.elasticsearch = None

            
