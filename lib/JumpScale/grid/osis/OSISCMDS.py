from JumpScale import j
import JumpScale.baselib.elasticsearch
import ujson

class OSISCMDS(object):

    def __init__(self, daemon):
        self.daemon = daemon
        self.osisInstances = {}  # key is namespace_categoryname
        self.db = None  # default db
        self.elasticsearch = None  # default elastic search connection
        self.path="/opt/jumpscale/apps/osis/logic"

    def authenticate(self, namespace, categoryname, name,passwd, session=None):
        """
        authenticates a user and returns the groups in which the user is
        """
        if namespace<>"system" and categoryname<>"user":
            raise RuntimeError("Cannot process, only supported for system/user namespace")
        oi = self._getOsisInstanceForCat("system", "user")

        key="%s_%s"%(j.application.whoAmI.gid,name)
        if not oi.exists(key):
            return {"authenticated":False,"exists":False,"groups":[]}

        user=ujson.loads(oi.get(key))

        if user["passwd"]==j.tools.hash.md5_string(passwd) or user["passwd"]==passwd:
            return {"authenticated":True,"exists":True,"groups":user["groups"]}

        return {"authenticated":False,"exists":True,"groups":[]}

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

    def set(self, namespace, categoryname, key=None, value=None, session=None):
        oi = self._getOsisInstanceForCat(namespace, categoryname)
        if oi.auth<>None:
            if oi.auth.authenticate(oi,"set",session.user,session.passwd)==False:
                raise RuntimeError("Authentication error on get %s_%s for user %s"%(namespace,categoryname,session.user))
        return oi.set(key=key, value=value)

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
            if passwd==j.core.osis.superadminpasswd:
                return True
            if j.tools.hash.md5_string(passwd)==j.core.osis.superadminpasswd:
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

        path = j.system.fs.joinPaths(self.path, name)

        self._initDefaultContent( namespacename=name)
        self.init(path=self.path, namespacename=name, template=template)
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
        self.elasticsearch.delete_index(key)
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

    def init(self, path="",overwriteImplementation=False, namespacename=None, template=None,session=None):
        if session<>None:
            self._authenticateAdmin(session)

        if path == "":
            path = "logic"

        self.path = path

        j.logger.consoleloglevel = 7

        if namespacename == None:
            for namespacename in j.system.fs.listDirsInDir(path, dirNameOnly=True):
                self.init(path, overwriteImplementation=overwriteImplementation, namespacename=namespacename)
        else:
            # te=j.core.taskletengine.get(j.system.fs.joinPaths("systemtasklets","init"))
            # te.executeV2(osis=self) #will add db & elasticsearch w
            if namespacename[0] == "_":
                return

            self._initDefaultContent(namespacename=namespacename)
            # enable db's
            if j.application.config.get("osis.db.type") == "filesystem":
                self.db = j.db.keyvaluestore.getFileSystemStore("osis")
            else:
                raise RuntimeError("Only filesystem db implemented in osis")

            # wait for elastic search & get
            eip=j.application.config.get("osis.elasticsearch.ip")
            eport=j.application.config.get("osis.elasticsearch.port")
            self.elasticsearch = j.clients.elasticsearch.get(ip=eip, port=int(eport))
            j.core.osis.db = self.db
            j.core.osis.elasticsearch = self.elasticsearch

            namespacepath = j.system.fs.joinPaths(path, namespacename)

            for catname in j.system.fs.listDirsInDir(namespacepath, dirNameOnly=True):
                catpath = j.system.fs.joinPaths(namespacepath, catname)

                # check if there is already an implfile
                implfile = "OSIS_%s_impl.py" % catname
                implpath = j.system.fs.joinPaths(catpath, implfile)
                fileFrom = j.system.fs.joinPaths(namespacepath, "OSIS_category_template.py")
                if overwriteImplementation or not j.system.fs.exists(path=implpath):
                    j.system.fs.copyFile(fileFrom, implpath)

                classs = j.core.osis._loadModuleClass(implpath)
                
                          
                if namespacename[0] <> "_":
                    osis = classs()
                    osis.init(catpath,namespace=namespacename, categoryname=catname)
                    key = "%s_%s" % (namespacename, catname)
                    self.osisInstances[key] = osis

            j.core.osis.db = None
            j.core.osis.elasticsearch = None

            
