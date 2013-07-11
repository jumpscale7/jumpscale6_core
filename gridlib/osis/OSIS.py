from OpenWizzy import o

class OSIS:
    """
    """
    def __init__(self):
        self.osisInstances={} #key is namespaceid_categoryid
        self.namespaceId2namespaceName={}
        self.categoryId2categoryName={}
        self.namespaceName2namespaceId={}
        self.categoryName2categoryId={}
        self.db=None #default db
        self.elasticsearch=None  #default elastic search connection        
        self.loadCoreHRD()

    def loadCoreHRD(self):
        idpath = o.system.fs.joinPaths('cfg', 'id.hrd')
        if not o.system.fs.exists(idpath):
            idcontent = "namespace.lastid=10" # start at 10
            o.system.fs.writeFile(idpath, idcontent)
        self.corehrd = o.core.hrd.getHRDTree("cfg")

    def get(self,namespaceid,categoryid):
        fullname="%s_%s" % (namespaceid,categoryid)
        if self.osisInstances.has_key(fullname):
            return self.osisInstances[fullname]
        o.errorconditionhandler.raiseBug(message="cannot find osis local instance for namespaceid:%s & categoryid:%s"%(namespaceid,categoryid),category="osis.valueerror")    

    def getFromName(self,namespaceName,categoryName):
        namespaceid=self.namespaceName2namespaceId[namespaceName]
        categoryid=self.categoryName2categoryId[categoryName]
        return self.get(namespaceid,categoryid)

    def incrementNamespaceId(self):
        lastid=self.corehrd.getInt("namespace.lastid")+1
        if lastid<10:
            lastid=11
        self.corehrd.set("namespace.lastid",lastid)
        return lastid

    def createNamespace(self,name=None,incrementName=False,nsid=0,template=None):
        """
        @param if name==None then auto id will be generated and name same as id
        """
        if name == None:
            name=str(self.incrementNamespaceId())
            id=int(name)
        elif incrementName and nsid==0:
            id=self.incrementNamespaceId()
            name+=str(id)
        elif incrementName and nsid<>0:
            id=nsid
            name+=str(id)
        else:
            id=None

        o.system.fs.createDir(o.system.fs.joinPaths(self.path,name))
        if template<>None:
            o.system.fs.copyDirTree(o.system.fs.joinPaths(self.path,"_%s"%template),o.system.fs.joinPaths(self.path,name),overwriteFiles=False)
            o.system.fs.remove(o.system.fs.joinPaths(self.path,name,"namespace.hrd"))
            o.system.fs.remove(o.system.fs.joinPaths(self.path,name,"namespaceid.hrd"))

        path = o.system.fs.joinPaths(self.path, name)
        if id<>None:
            self._initDefaultContent(overwriteHRD=False,namespacename=name)
            hrd=o.core.hrd.getHRDTree(path)
            hrd.set("namespace.id",id)

        self.init(path=self.path,overwriteHRD=False,namespacename=name,template=template)

        return [name,id]

    def listNamespaces(self,prefix=""):
        ddirs=o.system.fs.listDirsInDir(self.path,dirNameOnly=True)
        if prefix != "":
            ddirs=[item for item in ddirs if item.find(prefix)==0]
        return ddirs
    
    def listNamespaceCategories(self, namespacename):
        ddirs = o.system.fs.listDirsInDir(o.system.fs.joinPaths(self.path,
            namespacename), dirNameOnly = True)
        return ddirs

    def createNamespaceCategory(self,namespacename,name=None,catid=None):
        """
        @param if name==None then auto id will be generated and name same as id
        """
        namespacepath=o.system.fs.joinPaths(self.path,namespacename)
        if not o.system.fs.exists(path=namespacepath):
            self.createNamespace(namespacename)
        o.system.fs.createDir(o.system.fs.joinPaths(namespacepath,name))
        if catid<>None:
            self._initDefaultContent(overwriteHRD=False,overwriteTasklets=False,namespacename=namespacename)
            catpath=o.system.fs.joinPaths(self.path,namespacename,name)
            hrd=o.core.hrd.getHRDTree(catpath)
            hrd.set("category.id",catid)
        self.init(path=self.path, overwriteHRD=False, overwriteImplementation=False, namespacename=namespacename)

    def _initDefaultContent(self,overwriteHRD=False,namespacename=None):
        path=self.path
        if namespacename==None:
            for namespacename in o.system.fs.listDirsInDir(path, dirNameOnly=True):
                self._initDefaultContent(overwriteHRD,namespacename=namespacename)

        else:
            templatespath="_templates"
            templatespath_namespace=o.system.fs.joinPaths(templatespath,"namespace")
            templatespath_category=o.system.fs.joinPaths(templatespath,"category")
            namespacepath=o.system.fs.joinPaths(path,namespacename)
            o.system.fs.copyDirTree(templatespath_namespace,namespacepath,overwriteFiles=overwriteHRD)
            if namespacename[0]<>"_" and o.system.fs.exists(path=o.system.fs.joinPaths(namespacepath,".parentInTemplate")): #check if parent is coming from template
                o.system.fs.remove(o.system.fs.joinPaths(namespacepath,"OSIS_parent.py"))
                o.system.fs.remove(o.system.fs.joinPaths(namespacepath,"OSIS_parent.pyc"))

            for catname in o.system.fs.listDirsInDir(namespacepath, dirNameOnly=True):
                catpath=o.system.fs.joinPaths(namespacepath,catname)
                o.system.fs.copyDirTree(templatespath_category,catpath,overwriteFiles=overwriteHRD)
                # o.system.fs.copyDirTree(templatespath_osistasklets,catpath,overwriteFiles=overwriteTasklets)


    def init(self,path="",overwriteHRD=False,overwriteImplementation=False,namespacename=None,template=None):

        if path=="":
            path="logic"

        self.path=path

        o.logger.consoleloglevel=7


        if namespacename==None:
            for namespacename in o.system.fs.listDirsInDir(path, dirNameOnly=True):
                self.init(path,overwriteHRD,overwriteImplementation,namespacename=namespacename)
            
        else:

            # te=o.core.taskletengine.get(o.system.fs.joinPaths("systemtasklets","init"))
            # te.executeV2(osis=self) #will add db & elasticsearch w
            if namespacename[0]=="_":
                return
            self._initDefaultContent(overwriteHRD,namespacename=namespacename)
            hrd=self.corehrd
            hrd.add2tree(path) 
            hrd2=hrd.getHrd("")

            #enable db's
            if hrd2.osis_db_type=="filesystem":
                self.db=o.db.keyvaluestore.getFileSystemStore("osis")
            else:
                raise RuntimeError("Only filesystem db implemented in osis")

            #wait for elastic search & get
            self.elasticsearch= o.clients.elasticsearch.get(ip=hrd2.osis_elasticsearch_ip, port=int(hrd2.osis_elasticsearch_port))
            o.core.osis.db=self.db
            o.core.osis.elasticsearch=self.elasticsearch

            namespacepath=o.system.fs.joinPaths(path,namespacename)
            hrdNameSpace=hrd.getHrd("%s"%(namespacename))
            if not hrdNameSpace.get("namespace.id", True): #cannot be getInt because 0 is valid for system namespace
                hrdNameSpace.set("namespace.id",self.incrementNamespaceId())

            if not hrdNameSpace.get("namespace.name", True): 
                hrdNameSpace.set("namespace.name",namespacename)

            namespaceid=hrdNameSpace.getInt("namespace.id")
            self.namespaceId2namespaceName[namespaceid]=namespacename
            self.namespaceName2namespaceId[namespacename]=namespaceid
            
            if template<>None:
                hrdNameSpace.set("namespace.type", template)

            for catname in o.system.fs.listDirsInDir(namespacepath, dirNameOnly=True):
                hrdCat=hrd.getHrd("%s/%s"%(namespacename,catname))
                catpath=o.system.fs.joinPaths(namespacepath,catname)
                catid=hrdCat.getInt("category.id")
                if catid==0:
                    #need to find id for category
                    catid=hrdNameSpace.getInt("category.lastid")+1
                    hrdNameSpace.set("category.lastid",catid)
                    hrdCat.set("category.id",catid)

                if hrdCat.get("category.name")=="":
                    hrdCat.set("category.name",catname)

                self.categoryId2categoryName[catid]=catname
                self.categoryName2categoryId[catname]=catid

                key="%s_%s"%(namespaceid,catid)

                #check if there is already an implfile
                implfile="OSIS_%s_impl.py"%catname
                implpath=o.system.fs.joinPaths(catpath,implfile)
                fileFrom=o.system.fs.joinPaths(namespacepath,"OSIS_category_template.py")
                if overwriteImplementation or not o.system.fs.exists(path=implpath):
                    o.system.fs.copyFile(fileFrom, implpath)
                
                classs=o.core.osis._loadModuleClass(implpath)
                if namespacename[0]<>"_":
                    osis=classs()
                    osis.init(catpath,hrdCat)
                    self.osisInstances[key]=osis

            o.core.osis.db=None
            o.core.osis.elasticsearch=None


                

