from JumpScale import j

class PythonPackage(object):
    def __init__(self):
        self._checked=False
        self._usrPathCache=[]
        self._pythonPathCache=[]

    def clearcache(self):
        print "CLEARCACHE"
        self.__init__()

    def _getPythonPathNames(self):
        print "getpython path names"
        if self._pythonPathCache==[]:
            for path in j.application.config.getItemsFromPrefix("python.paths"):
                for item in j.system.fs.listFilesAndDirsInDir(path,recursive=True):
                    item=item.lower()
                    self._pythonPathCache.append(item)   
            self._pythonPathCache.sort()    
        return  self._pythonPathCache

    def _getUsrPathNames(self):
        print "getpython path names"
        if self._usrPathCache==[]:
            for path in j.application.config.getItemsFromPrefix("python.paths"):
                for item in j.system.fs.listFilesAndDirsInDir(path,recursive=True):
                    item=item.lower()
                    self._usrPathCache.append(item)   
            self._usrPathCache.sort()  
        return  self._usrPathCache

    def check(self):
        if self._checked:
            return
        if not j.application.config.exists("python.paths.local.sitepackages"):
            print "need to deploy python package jpackage"
            p=j.packages.get("jpackagesbase","python","2.7")
            p.reinstall()
        self._checked=True

    def install(self, name, version=None):
        self.check()
        if version:
            j.system.process.execute("pip install '%s%s'" % (name, version))
        j.system.process.execute("pip install '%s' --upgrade" % name)

    def remove(self,names,clearcache=True):
        """
        @param names can be 1 name as str or array when list
        will look in all possible python paths & remove the python lib
        """
        if j.basetype.list.check(names):
            for name in names:
                self.remove(name,clearcache=False)
            self.clearcache()
        else:
            self.check()
            name2=names.lower().strip()
            # name2=name2.replace("python","")
            res=j.system.platform.ubuntu.findPackagesInstalled(name2)
            ok=False
            for item in res:
                item2=item.lower().strip()
                if item2.find("python")<>-1 or item2.find("py")==0:
                    #found python package installed through aptget, remove
                    j.system.platform.ubuntu.remove(item)
                    ok=True
            if res<>[] and ok==False:
                from IPython import embed
                print "DEBUG NOW remove python package, debug, found no python package but something else"
                print "package:%s"%name
                print "found packages on ubuntu which match name:\n%s"%res
                embed()            
            
            #get paths from python out of config
            # print "FIND TO REMOVE:%s"%name2
            for path in self._getUsrPathNames():
                if path.find(name2)<>-1:
                    if path.find("ipython")==-1:                        
                        try:
                            j.system.fs.remove(path, onlyIfExists=True)
                            # print "removed:%s"%path
                        except:
                            pass

                # print "remove %s from python dir:%s"%(name,path)
            if clearcache:
                self.clearcache()

    def getSitePackagePathLocal(self):
        self.check()
        return j.application.config.get("python.paths.local.sitepackages")

    def copyLibsToLocalSitePackagesDir(self,rootpath):
        """
        list all dirs in specified path and for each dir call
        self.copyLibToLocalSitePackagesDir
        """
        self.check()
        for item in j.system.fs.listDirsInDir(rootpath):
            self.copyLibToLocalSitePackagesDir(item)

    def copyLibToLocalSitePackagesDir(self,path,remove=True):
        """
        copy library to python.paths.local.sitepackages config param in main jumpscale hrd 
        eg. for ubuntu is: /usr/local/lib/python2.7/site-packages/
        does this for 1 lib, so the dir needs to be the library by itself
        """
        self.check()
        sitepackagepath=self.getSitePackagePathLocal()
        base=j.system.fs.getBaseName(path)
        dest=j.system.fs.joinPaths(sitepackagepath,base)
        if remove:
            self.remove(base)
        j.logger.log("copy python lib from %s to %s"%(path,dest),5,category="python.install")
        j.system.fs.copyDirTree(path,dest, keepsymlinks=False, eraseDestination=True, skipProtectedDirs=False, overwriteFiles=True)

