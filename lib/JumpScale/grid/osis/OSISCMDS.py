from JumpScale import j
import JumpScale.baselib.elasticsearch

class OSISCMDS(object):

    def __init__(self, daemon):
        self.daemon = daemon
        self.osisInstances = {}  # key is namespace_categoryname
        self.db = None  # default db
        self.elasticsearch = None  # default elastic search connection
        self._loadCoreHRD()
        self.path="/opt/jumpscale/apps/osis/logic"

    def get(self, namespace, categoryname, key, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        return oi.get(key)

    def set(self, namespace, categoryname, key=None, value=None, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        return oi.set(key=key, value=value)

    def delete(self, namespace, categoryname, key, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        return oi.delete(key=key)

    def search(self, namespace, categoryname, query, start=0, size=None, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        result = oi.find(query, start, size)
        return result

    def list(self, namespace, categoryname, prefix, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        return oi.list(prefix)

    def echo(self, msg="", session=None):
        return msg

    #################################################3

    def _loadCoreHRD(self,session=None):
        self.corehrd = j.core.hrd.getHRD("cfg")

    def _getOsisInstanceForCat(self, namespace, category):
        fullname = "%s_%s" % (namespace, category)
        if self.osisInstances.has_key(fullname):
            return self.osisInstances[fullname]
        from IPython import embed
        print "DEBUG NOW did not find category"
        embed()
        
        j.errorconditionhandler.raiseBug(
            message="cannot find osis local instance for namespace:%s & category:%s" % (namespace, category), die=False, \
            category="osis.valueerror")

    def _authenticateAdmin(self,session):
        if session.user=="root" and session.passwd=="rooter":
            #@todo needs to come from a local hrd
            return True
        else:
            raise RuntimeError("Could not authenticate administrator.")

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
            j.system.fs.remove(j.system.fs.joinPaths(self.path, name, "namespace.hrd"))
            j.system.fs.remove(j.system.fs.joinPaths(self.path, name, "namespaceid.hrd"))

        path = j.system.fs.joinPaths(self.path, name)

        self._initDefaultContent(overwriteHRD=False, namespacename=name)
        hrd = j.core.hrd.getHRD(path)
        self.init(path=self.path, overwriteHRD=False, namespacename=name, template=template)
        return True

    def getOsisObjectClass(self,namespace,categoryname,session=None):
        path=j.system.fs.joinPaths(self.path, namespace,categoryname,"model.py")
        if j.system.fs.exists(path):
            return j.system.fs.fileGetContents(path)
        else:
            return ""

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

    def createNamespaceCategory(self, namespacename, name,session=None):
        """
        """
        if session<>None:
            self._authenticateAdmin(session)
        namespacepath = j.system.fs.joinPaths(self.path, namespacename)
        if not j.system.fs.exists(path=namespacepath):
            raise RuntimeError("Could not find namespace with name:%s"%namespacename)

        j.system.fs.createDir(j.system.fs.joinPaths(namespacepath, name))

        self.init(path=self.path, overwriteHRD=False, overwriteImplementation=False, namespacename=namespacename)

    def _initDefaultContent(self, overwriteHRD=False, namespacename=None):
        path = self.path
        if namespacename == None:
            for namespacename in j.system.fs.listDirsInDir(path, dirNameOnly=True):
                self._initDefaultContent(overwriteHRD, namespacename=namespacename)

        else:
            templatespath = "_templates"
            templatespath_namespace = j.system.fs.joinPaths(templatespath, "namespace")
            templatespath_category = j.system.fs.joinPaths(templatespath, "category")
            namespacepath = j.system.fs.joinPaths(path, namespacename)
            j.system.fs.copyDirTree(templatespath_namespace, namespacepath, overwriteFiles=overwriteHRD)
            if namespacename[0] <> "_" and j.system.fs.exists(path=j.system.fs.joinPaths(namespacepath, ".parentInTemplate")):  
                # check if parent is coming from template
                j.system.fs.remove(j.system.fs.joinPaths(namespacepath, "OSIS_parent.py"))
                j.system.fs.remove(j.system.fs.joinPaths(namespacepath, "OSIS_parent.pyc"))

            for catname in j.system.fs.listDirsInDir(namespacepath, dirNameOnly=True):
                catpath = j.system.fs.joinPaths(namespacepath, catname)
                j.system.fs.copyDirTree(templatespath_category, catpath, overwriteFiles=overwriteHRD)
                # j.system.fs.copyDirTree(templatespath_osistasklets,catpath,overwriteFiles=overwriteTasklets)

    def init(self, path="", overwriteHRD=False, overwriteImplementation=False, namespacename=None, template=None,session=None):
        if session<>None:
            self._authenticateAdmin(session)

        if path == "":
            path = "logic"

        self.path = path

        j.logger.consoleloglevel = 7

        if namespacename == None:
            for namespacename in j.system.fs.listDirsInDir(path, dirNameOnly=True):
                self.init(path, overwriteHRD, overwriteImplementation, namespacename=namespacename)
        else:
            # te=j.core.taskletengine.get(j.system.fs.joinPaths("systemtasklets","init"))
            # te.executeV2(osis=self) #will add db & elasticsearch w
            if namespacename[0] == "_":
                return

            self._initDefaultContent(overwriteHRD, namespacename=namespacename)
            hrd = self.corehrd
            
            hrd.add2tree(path)
            hrd2 = hrd.getHrd("")

            # enable db's
            if hrd2.osis_db_type == "filesystem":
                self.db = j.db.keyvaluestore.getFileSystemStore("osis")
            else:
                raise RuntimeError("Only filesystem db implemented in osis")

            # wait for elastic search & get
            self.elasticsearch = j.clients.elasticsearch.get(ip=hrd2.osis_elasticsearch_ip, port=int(hrd2.osis_elasticsearch_port))
            j.core.osis.db = self.db
            j.core.osis.elasticsearch = self.elasticsearch

            namespacepath = j.system.fs.joinPaths(path, namespacename)
            hrdNameSpace = hrd.getHrd("%s" % (namespacename))

            if not hrdNameSpace.get("namespace.name")==namespacename:
                hrdNameSpace.set("namespace.name", namespacename)

            if template <> None:
                hrdNameSpace.set("namespace.type", template)

            for catname in j.system.fs.listDirsInDir(namespacepath, dirNameOnly=True):
                hrdCat = hrd.getHrd("%s/%s" % (namespacename, catname))
                catpath = j.system.fs.joinPaths(namespacepath, catname)

                if hrdCat.get("category.name") <>catname:
                    hrdCat.set("category.name", catname)

                # check if there is already an implfile
                implfile = "OSIS_%s_impl.py" % catname
                implpath = j.system.fs.joinPaths(catpath, implfile)
                fileFrom = j.system.fs.joinPaths(namespacepath, "OSIS_category_template.py")
                if overwriteImplementation or not j.system.fs.exists(path=implpath):
                    j.system.fs.copyFile(fileFrom, implpath)

                classs = j.core.osis._loadModuleClass(implpath)
                if namespacename[0] <> "_":
                    osis = classs()
                    osis.init(catpath, hrdCat)
                    key = "%s_%s" % (namespacename, catname)
                    self.osisInstances[key] = osis

            j.core.osis.db = None
            j.core.osis.elasticsearch = None

            
