
from JumpScale import j

class _RecipeItem:
    '''Ingredient of a CodeRecipe'''
    def __init__(self, coderepoConnection, source, destination,platform=None, systemdest=None,type=None):
        self.coderepoConnection = coderepoConnection
        self.source = source
        self.destination=destination
        self.platform=platform
        self.systemdest = systemdest or j.system.fs.joinPaths(j.dirs.baseDir, destination)
        self.type=type
        
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

    def exportToSystem(self,force=True):
        '''
        Copy files from coderepo to destination, without metadata of coderepo
        This is only done when the recipe item is relevant for our platform
        '''
        self._log("export to system.","export")

        if self._isPlatformSupported:
            source = j.system.fs.joinPaths(self.coderepoConnection.basedir, self.source)
            destination = self.systemdest
            print "export:%s to %s"%(source,destination)
            if j.system.fs.isLink(destination):
                j.system.fs.remove(destination)   
            else:
                if j.system.fs.exists(destination) and force==False:
                    if j.application.shellconfig.interactive:                            
                        if not j.gui.dialog.askYesNo("\nDo you want to overwrite %s" % destination, True):
                            j.gui.dialog.message("Not overwriting %s, item will not be exported" % destination)
                            return        
    
                self._removeDest(destination)  
            j.system.fs.copyDirTree(source, destination)
                             
        
    def _copy(self, src, dest):
        if j.system.fs.isFile(src):
            destDir = j.system.fs.getDirName(dest)
            j.system.fs.createDir(destDir)
            j.system.fs.copyFile(src, dest)
        elif j.system.fs.isDir(src):            
            j.system.fs.copyDirTree(src, dest)
        else:
            raise RuntimeError("Cannot handle destination %s %s\n Did you codecheckout your code already? Code was not found to package." % (src, dest))


    def codeToFiles(self, jpackage, platform):
        """
        copy code from repo's (using the recipes) to the file location
        example /opt/qbase5/var/jpackages/files/jpackages/trac/0.12/generic/
        this is done per platform
        """

        self._log("code to files for %s for platform:%s"%(jpackage,platform),category="codetofiles")
        
        if not self.coderepoConnection:
            raise RuntimeError("Cannot  copy code to files because no repo is defined")                    

        src=j.system.fs.joinPaths(self.coderepoConnection.basedir,self.source)

        if self.destination.startswith('/'):
            destSuffix = self.destination[1:]                
        else:
            destSuffix = self.destination
        
        platformFilesPath = jpackage.getPathFilesPlatform(platform)
        dest = j.system.fs.joinPaths(platformFilesPath, destSuffix)
        self._copy(src, dest)

        
    def importFromSystem(self, jpackages):
        """
        this packages from existing system and will only work for specified platform
        import from system to files
        """
        self._log("import from system.","import")
        if self._isPlatformSupported:
            if self.coderepoConnection:
                raise RuntimeError("Cannot import from system because, qp code recipe is used for a coderepo, coderepo should be None")            

            if self.destination.startswith('/'):
                src = self.destination                        
                destSuffix = self.destination[1:]                
            else:
                src = j.system.fs.pathNormalize(self.destination,j.dirs.baseDir) 
                destSuffix = self.destination
            
            platformFilesPath = jpackages.getPathFilesPlatform(self.platform)
            dest = j.system.fs.joinPaths(platformFilesPath, destSuffix)
            
            self._removeDest(dest)
            self._copy(src, dest)
        else:
            raise RuntimeError("Platform is not supported.")
        
    def linkToSystem(self,force=False):
        '''
        link parts of the coderepo to the destination and put this  entry in the protected dirs section so data cannot be overwritten by jpackages
        '''
        self._log("link to system",category="link")
        
        if self.type=="config":
            return self.exportToSystem()
        if self._isPlatformSupported:
            source = j.system.fs.joinPaths(self.coderepoConnection.basedir, self.source)
            destination = self.systemdest
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
        return "%s from:%s to:%s" %(self.coderepoConnection,self.source,self.destination)
    
    def __repr__(self):
        return self.__str__()


class CodeManagementRecipe:
    '''
    Recipe providing guidelines how to cook a JPackage from source code in
    '''
    def __init__(self):
        self.items = []


    def add(self, coderepoConnection, sourcePath, destinationPath,platform=None, systemdest=None,type=None):
        '''Add a source (ingredient) to the recipe
        '''
        self.items.append(_RecipeItem(coderepoConnection, sourcePath, destinationPath,platform, systemdest,type=type))

    def export(self):
        '''Export all items from VCS to the system sandbox or other location specifed'''
        for item in self.items:
            item.exportToSystem()
            
    def link(self,force=False):
        for item in self.items:
            item.linkToSystem(force=force)    
            
    def importFromSystem(self,jpackages):
        """
        go from system to files section
        """
        for item in self.items:
            item.importFromSystem(jpackages)                

    def package(self, jpackage, platform):
        # clean up files
        # filesPath = jpackages.getPathFiles()
        # j.system.fs.removeDirTree(filesPath)
        ##DO TNO REMOVE, TOO DANGEROUS HAPPENS NOW PER ITEM

        for item in self.items:
            item.codeToFiles(jpackage, platform)
        
    def push(self):
        for item in self.items:
            item.push()       
            
    def update(self,force=False):        
        return self.pullupdate(force=force)
    
    def pullupdate(self,force=False):
        repoconnections = self._getRepoConnections()
        for repoconnection in repoconnections:
            #item.pullupdate(force=force)    
            repoconnection.pullupdate()

    def pullmerge(self):
        repoconnections = self._getRepoConnections()
        for repoconnection in repoconnections:
            #item.pullupdate(force=force)    
            repoconnection.pullmerge()        
            
    def commit(self):
        repoconnections = self._getRepoConnections()
        for repoconnection in repoconnections:
            #item.pullupdate(force=force)    
            repoconnection.commit()                

    # def identify(self):
    #     repoconnections = self._getRepoConnections()
    #     identities = {}
    #     for repoconnection in repoconnections:
    #         identity = repoconnection.identify()
    #         key = repoconnection.repokey
    #         if not key:
    #             raise ValueError("Repository %s has no valid repokey" %
    #                     repoconnection)
    #         identities[key] = identity

    #     return identities

    def _getRepoConnections(self):
        repoconnections = []
        for item in self.items:
            if item.coderepoConnection not in repoconnections:
                repoconnections.append(item.coderepoConnection)
        return repoconnections

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

