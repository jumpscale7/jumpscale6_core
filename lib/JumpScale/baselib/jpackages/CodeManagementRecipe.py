
from JumpScale import j

class RecipeItem(object):
    '''Ingredient of a CodeRecipe'''
    def __init__(self, repoinfo,source, destination,platform="generic",type="base",tags=""):
        """
        @param types sitepackages, root, base, etc, tmp,bin
        @param tagslabels: e.g. config as str
        """
        self.repoinfo=repoinfo
        self.source = source.strip().strip("/")

        self.destination=destination.strip().strip("/")
        if self.destination=="":
            self.destination=self.source

        if platform=="":
            platform="generic"

        self.platform=platform

        self.type=type.lower().strip()

        if self.type=="sitepackages":
            base=j.application.config.get("python.paths.local.sitepackages")
            self.systemdest = j.system.fs.joinPaths(base, self.destination)
        elif self.type=="root":
            self.systemdest = destination
        elif self.type=="base":
            self.systemdest = j.system.fs.joinPaths(j.dirs.baseDir, self.destination)
        elif self.type=="etc":
            base="/etc"
            self.systemdest = j.system.fs.joinPaths(base, self.destination)
        elif self.type=="tmp":
            self.systemdest = j.system.fs.joinPaths(j.dirs.tmpDir, self.destination)
        elif self.type=="bin":
            base=j.application.config.get("bin.local")
            self.systemdest = j.system.fs.joinPaths(base, self.destination)
        else:
            base=j.application.config.applyOnContent(self.type)
            self.systemdest = j.system.fs.joinPaths(base, self.destination)
        
        self.tags=j.core.tags.getObject(tags)
        
        # determine supported platforms 
        hostPlatform = j.system.platformtype.myplatform
        supportedPlatforms = list()

        supportedPlatforms = j.system.platformtype.getParents(hostPlatform)
        if not platform:
            self._isPlatformSupported = hostPlatform in supportedPlatforms
        else:
            self._isPlatformSupported = self.platform in supportedPlatforms

    def _log(self,message,category="",level=5):
        message="recipeitem:%s-%s  %s" % (self.source,self.destination,message)
        category="recipeitem.%s"%category
        category=category.rstrip(".")
        j.packages.log(message,category,level)     

    def getSource(self):
        account=self.repoinfo.get("jp.code.account")
        repo=self.repoinfo.get("jp.code.repo")
        ttype=self.repoinfo.get("jp.code.type")
        if ttype<>"bitbucket":
            raise RuntimeError("only bitbucket repo's supported.")        
        return j.system.fs.joinPaths(j.dirs.codeDir,account,repo,self.source)

    def exportToSystem(self,force=True):
        '''
        Copy files from coderepo to destination, without metadata of coderepo
        This is only done when the recipe item is relevant for our platform
        '''
        self._log("export to system.","export")

        if self._isPlatformSupported:
            source = self.getSource()
            destination = self.systemdest
            print "export:%s to %s"%(source,destination)
            if j.system.fs.isLink(destination):
                j.system.fs.remove(destination)   
                j.dirs.removeProtectedDir(destination)
            else:
                if j.system.fs.exists(destination) and force==False:
                    if j.application.shellconfig.interactive:                            
                        if not j.gui.dialog.askYesNo("\nDo you want to overwrite %s" % destination, True):
                            j.gui.dialog.message("Not overwriting %s, item will not be exported" % destination)
                            return        
                self._removeDest(destination)  
            if j.system.fs.isFile(source):
                j.system.fs.copyFile(source, destination,skipProtectedDirs=True)
            else:
                j.system.fs.copyDirTree(source, destination,skipProtectedDirs=True)
                             
        
    def _copy(self, src, dest):
        if not j.system.fs.exists(src):
            raise RuntimeError("Cannot find:%s for recipeitem:%s"%(src,self))
        
        if j.system.fs.isFile(src):
            destDir = j.system.fs.getDirName(dest)
            j.system.fs.createDir(destDir,skipProtectedDirs=True)
            j.system.fs.copyFile(src, dest,skipProtectedDirs=True)
        elif j.system.fs.isDir(src):            
            j.system.fs.copyDirTree(src, dest,skipProtectedDirs=True)
        else:
            raise RuntimeError("Cannot handle destination %s %s\n Did you codecheckout your code already? Code was not found to package." % (src, dest))

    def codeToFiles(self, jpackage):
        """
        copy code from repo's (using the recipes) to the file location for packaging
        this is done per platform as specified in recipe, if not specified then generic
        """

        self._log("package code to files for %s"%(jpackage),category="codetofiles")        
        src = self.getSource()        
        platformFilesPath = jpackage.getPathFilesPlatform(self.platform)
        dest = j.system.fs.joinPaths(platformFilesPath, "cr_%s"%self.type ,self.destination)
        self._removeDest(dest)
        self._copy(src, dest)
        
    # def importFromSystem(self, jpackages):
    #     """
    #     this packages from existing system and will only work for specified platform
    #     import from system to files
    #     """
    #     self._log("import from system.","import")
    #     if self._isPlatformSupported:
    #         if self.coderepoConnection:
    #             raise RuntimeError("Cannot import from system because, jp code recipe is used for a coderepo, coderepo should be None")            

    #         if self.destination.startswith('/'):
    #             src = self.destination                        
    #             destSuffix = self.destination[1:]                
    #         else:
    #             src = j.system.fs.pathNormalize(self.destination,j.dirs.baseDir) 
    #             destSuffix = self.destination
            
    #         platformFilesPath = jpackages.getPathFilesPlatform(self.platform)
    #         dest = j.system.fs.joinPaths(platformFilesPath, destSuffix)
            
    #         self._removeDest(dest)
    #         self._copy(src, dest)
    #     else:
    #         raise RuntimeError("Platform is not supported.")
        
    def linkToSystem(self,force=False):
        '''
        link parts of the coderepo to the destination and put this  entry in the protected dirs section so data cannot be overwritten by jpackages
        '''
        self._log("link to system",category="link")
        
        if self.type=="config":
            return self.exportToSystem()
        if self._isPlatformSupported:
            source = self.getSource()        
            destination = self.systemdest

            if self.tags.labelExists("config"):
                print "CONFIG:%s"%self
                self.exportToSystem(force=force)
            else:
                print "link:%s to %s"%(source,destination)
                if j.system.fs.isLink(destination):
                    j.system.fs.remove(destination)   
                else:
                    if j.system.fs.exists(destination) and force==False:
                        if j.application.shellconfig.interactive:                            
                            if not j.gui.dialog.askYesNo("\nDo you want to overwrite %s" % destination, True):
                                j.gui.dialog.message("Not overwriting %s, it will not be linked" % destination)
                                return        
        
                    self._removeDest(destination)
                j.system.fs.symlink(source, destination)
                j.dirs.addProtectedDir(destination)

    def unlinkSystem(self,force=False):
        '''
        unlink the system, remove the links and copy the content instead
        '''
        self._log("unlink system",category="link")
        
        if self.type=="config":
            return 

        if j.system.fs.isLink(self.systemdest):
            j.system.fs.remove(self.systemdest)
            j.dirs.removeProtectedDir(self.systemdest)

        self.exportToSystem(force=force)
        
    def _removeDest(self, dest):
        """ Remove a destionation file or directory."""
        isFile = j.system.fs.isFile
        isDir = j.system.fs.isDir
        removeFile = j.system.fs.remove
        removeDirTree = j.system.fs.removeDirTree
        exists = j.system.fs.exists

        if not exists(dest):
            return
        elif isFile(dest):
            removeFile(dest)
        elif isDir(dest):
            removeDirTree(dest)
        else:
            raise RuntimeError("Cannot remove destination of unknown type '%s'" % dest)

    def __str__(self):
        return "from:%s to:%s type:%s platf:%s tags:%s" %(self.source,self.destination,self.type,self.platform,self.tags)
    
    def __repr__(self):
        return self.__str__()


class CodeManagementRecipe:
    '''
    Recipe providing guidelines how to cook a JPackage from source code in a repo, is populated from a config file
    '''
    def __init__(self,hrdpath,configpath):
        self._repoconnection = None
        self.configpath=configpath
        self.hrd=j.core.hrd.getHRD(hrdpath)
        self.items = []
        self._process()

    def _getSource(self,source):
        account=self.hrd.get("jp.code.account")
        repo=self.hrd.get("jp.code.repo")
        ttype=self.hrd.get("jp.code.type")
        if ttype<>"bitbucket":
            raise RuntimeError("only bitbucket repo's supported.")        
        return j.system.fs.joinPaths(j.dirs.codeDir,account,repo,source)

    def _process(self):
        content=j.system.fs.fileGetContents(self.configpath)
        for line in content.split("\n"):
            line=line.strip()
            if line=="" or line[0]=="#":
                continue
            splitted= line.split("|")
            if len(splitted)<>5:
                raise RuntimeError("error in coderecipe config file: %s on line:%s"%(self.configpath,line))
            splitted=[item.strip() for item in splitted]
            source,dest,platform,ttype,tags=splitted
            if source.find("*")<>-1:
                source=source.replace("*","")
                source2=self._getSource(source)
                for item in j.system.fs.listFilesInDir(source2,recursive=False):
                    item=j.system.fs.getBaseName(item)                    
                    source3="%s/%s"%(source,item)
                    source3=source3.replace("//","/")
                    # print "*%s*"%source3
                    idest = j.system.fs.joinPaths(dest, item)
                    item=RecipeItem(self.hrd,source=source3, destination=idest,platform=platform,type=ttype,tags=tags)
                    self.items.append(item)                                                
                for item in j.system.fs.listDirsInDir(source2,recursive=False):
                    item=j.system.fs.getBaseName(item+"/")                    
                    idest = j.system.fs.joinPaths(dest, item)
                    source3="%s/%s"%(source,item)
                    source3=source3.replace("//","/")
                    source3=source3.replace("//","/")
                    # print "*%s*"%source3
                    item=RecipeItem(self.hrd,source=source3, destination=idest,platform=platform,type=ttype,tags=tags)
                    self.items.append(item) 
            else:
                item=RecipeItem(self.hrd,source=source, destination=dest,platform=platform,type=ttype,tags=tags)
                self.items.append(item)

    def export(self):
        '''Export all items from VCS to the system sandbox or other location specifed'''
        repoconnection = self._getRepoConnection()
        for item in self.items:
            item.exportToSystem()
            
    def link(self,force=False):
        repoconnection = self._getRepoConnection()
        for item in self.items:
            item.linkToSystem(force=force)    

    def unlink(self,force=False):
        for item in self.items:
            item.unlinkSystem(force=force)    

    # def importFromSystem(self,jpackages):
    #     """
    #     go from system to files section
    #     """
    #     for item in self.items:
    #         item.importFromSystem(jpackages)                

    def package(self, jpackage,*args,**kwargs):
        # clean up files
        # filesPath = jpackages.getPathFiles()
        # j.system.fs.removeDirTree(filesPath)
        ##DO TNO REMOVE, TOO DANGEROUS HAPPENS NOW PER ITEM
        repoconnection = self._getRepoConnection()
        for item in self.items:
            item.codeToFiles(jpackage)

        
    def push(self):
        repoconnection = self._getRepoConnection()
        for item in self.items:
            item.push()       
            
    def update(self,force=False):        
        repoconnection = self._getRepoConnection()
        return self.pullupdate(force=force)
    
    def pullupdate(self,force=False):
        repoconnection = self._getRepoConnection()
        repoconnection.pullupdate()

    def pullmerge(self):
        repoconnection = self._getRepoConnection()
        repoconnection.pullmerge()        
            
    def commit(self):
        repoconnection = self._getRepoConnection()
        repoconnection.commit()                


    def _getSource(self, source):
        con = self._getRepoConnection()
        return j.system.fs.joinPaths(con.basedir, source)

    def _getRepoConnection(self):
        if self._repoconnection:
            return self._repoconnection
        account=self.hrd.get("jp.code.account")
        repo=self.hrd.get("jp.code.repo")
        branch=self.hrd.get("jp.code.branch")
        ttype=self.hrd.get("jp.code.type")
        if ttype == "bitbucket":
            branch = branch or 'default'
            print "getrepo connection: %s %s %s"%(account, repo, branch)
            self._repoconnection = j.clients.bitbucket.getRepoConnection(account, repo, branch)
            return self._repoconnection
        # elif ttype == "github":
        #     pass
        else:
            raise RuntimeError("Connection of type %s not supported" % ttype)

    def isDestinationClean(self):
        '''Check whether the final destination is clean (means do the folders exist)

        Returns C{True} if none of the destination folders exist, C{False}
        otherwise.
        '''
        for item in self._items:
            if j.system.fs.exists(item.destination):
                return False

        return True

    def removeFromSystem(self):
        '''Remove all folders the recipe has written to'''
        for item in self._items:
            if j.system.fs.isDir(item.destination):
                j.system.fs.removeDirTree(item.destination)
            else:
                j.system.fs.remove(item.destination)

    def __str__(self):
        s="recipe:\n"
        for item in self.items:
            s+="- %s\n" % item
        return s
    
    def __repr__(self):
        return self.__str__()

