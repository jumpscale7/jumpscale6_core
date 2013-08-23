
from OpenWizzy import o

class _RecipeItem:
    '''Ingredient of a CodeRecipe'''
    def __init__(self, coderepoConnection, source, destination,platform=o.enumerators.PlatformType.GENERIC):
        self.coderepoConnection = coderepoConnection
        self.source = source
        self.destination=destination
        self.platform=platform
        
        # determine supported platforms 
        hostPlatform = o.system.platformtype
        supportedPlatforms = list()
                    
        while hostPlatform != None:
            supportedPlatforms.append(hostPlatform)
            hostPlatform = hostPlatform.parent
            
        self._isPlatformSupported = self.platform in supportedPlatforms

    def exportToSystem(self):
        '''
        Copy files from coderepo to destination, without metadata of coderepo
        This is only done when the recipe item is relevant for our platform
        '''

        if self._isPlatformSupported:
            codeOnSystem=o.system.fs.pathNormalize(self.destination,o.dirs.baseDir) 
            locationInRepo=o.system.fs.joinPaths(self.coderepoConnection.basedir,self.source)
                        
            if o.system.fs.exists(codeOnSystem):
                if o.application.shellconfig.interactive:
                    # In interactive mode, ask whether destination can be removed

                    if o.system.fs.isDir(codeOnSystem):
                        answer = o.gui.dialog.askYesNo(
                            'Export location %s exists. Do you want the folder to be removed before exporting?' % codeOnSystem)
                        if answer:
                            o.system.fs.removeDirTree(codeOnSystem)

                    elif o.system.fs.isFile(codeOnSystem):
                        answer = o.gui.dialog.askYesNo(
                            'Export location %s exists. Do you want the file to be removed before exporting?' % codeOnSystem)
                        if answer:
                            o.system.fs.removeFile(codeOnSystem)

                else:
                    raise RuntimeError('Export location %s exists' % codeOnSystem)

            if o.system.fs.isFile(locationInRepo):
                destDir = o.system.fs.getDirName(codeOnSystem)
                o.system.fs.createDir(destDir)
                if not o.system.fs.exists(codeOnSystem):
                    o.system.fs.copyFile(locationInRepo, codeOnSystem)
            elif o.system.fs.isDir(locationInRepo):
                if not o.system.fs.exists(codeOnSystem):
                    o.system.fs.copyDirTree(locationInRepo, codeOnSystem)            
        
    #def importt(self):
        ##@todo check is not a link (IMPORTANT)
        #codeOnSystem=o.system.fs.pathNormalize(self.destination,o.dirs.baseDir) 
        #locationInRepo=o.system.fs.joinPaths(self.coderepoConnection.basedir,self.source)
        #if o.system.fs.exists(locationInRepo):
            #if o.application.shellconfig.interactive:                            
                #if o.gui.dialog.askYesNo("\ndo you want to overwrite %s" % locationInRepo,True)==False:
                    #return
        #o.system.fs.removeDirTree(locationInRepo)
        #o.system.fs.copyDirTree(codeOnSystem, locationInRepo)        
        
    #def pullupdate(self,force=False, commitMessage=""):
        #self.coderepoConnection.pullupdate(force, commitMessage)
        
    #def pullmerge(self, commitMessage=""):
        #self.coderepoConnection.pullmerge( commitMessage)
    
    #def pushcommit(self,commitMessage="",ignorechanges=False,addRemoveUntrackedFiles=False,trymerge=True):
        #self.coderepoConnection.pushcommit(commitMessage,ignorechanges,addRemoveUntrackedFiles,trymerge)

    #def push(self):
        #self.coderepoConnection.push()        

    #def commit(self, message):
        #self.coderepoConnection.message()     
        
    def codeToFiles(self, owpackage, platform):
        """
        copy code from repo's (using the recipes) to the file location
        example /opt/qbase5/var/owpackages/files/owpackages/trac/0.12/generic/
        this is done per platform
        """
        
        if not self.coderepoConnection:
            raise RuntimeError("Cannot  copy code to files because no repo is defined")                    

        src=o.system.fs.joinPaths(self.coderepoConnection.basedir,self.source)

        if self.destination.startswith('/'):
            destSuffix = self.destination[1:]                
        else:
            destSuffix = self.destination
        
        platformFilesPath = owpackage.getPathFilesPlatform(self.platform)
        dest = o.system.fs.joinPaths(platformFilesPath, destSuffix)
        
        if o.system.fs.isFile(src):
            destDir = o.system.fs.getDirName(dest)
            o.system.fs.createDir(destDir)
            o.system.fs.copyFile(src, dest)
        elif o.system.fs.isDir(src):            
            o.system.fs.copyDirTree(src, dest)
        else:
            raise RuntimeError("Cannot handle destination %s %s\n Did you codecheckout your code already? Code was not found to package." % (src, dest))

        
    def importFromSystem(self, owpackage):
        """
        this packages from existing system and will only work for specified platform
        import from system to files
        """
        if self._isPlatformSupported:
            if self.coderepoConnection:
                raise RuntimeError("Cannot import from system because, qp code recipe is used for a coderepo, coderepo should be None")            

            if self.destination.startswith('/'):
                src = self.destination                        
                destSuffix = self.destination[1:]                
            else:
                src = o.system.fs.pathNormalize(self.destination,o.dirs.baseDir) 
                destSuffix = self.destination
            
            platformFilesPath = owpackage.getPathFilesPlatform(self.platform)
            dest = o.system.fs.joinPaths(platformFilesPath, destSuffix)
            
            self._removeDest(dest)
            if o.system.fs.isFile(src):
                destDir = o.system.fs.getDirName(dest)
                o.system.fs.createDir(destDir)
                o.system.fs.copyFile(src, dest)
            elif o.system.fs.isDir(src):
                o.system.fs.copyDirTree(src, dest)
            else:
                raise RuntimeError("Cannot handle destination %s %s\n Did you codecheckout your code already? Code was not found to package." % (src, dest))
        else:
            raise RuntimeError("Platform is not supported.")

        
    def linkToSystem(self):
        '''
        link parts of the coderepo to the destination and put this  entry in the protected dirs section so data cannot be overwritten by owpackages
        '''
        if self._isPlatformSupported:
            source = o.system.fs.joinPaths(self.coderepoConnection.basedir, self.source)
            destination = o.system.fs.pathNormalize(self.destination, o.dirs.baseDir)
            if o.system.fs.isLink(destination):
                o.system.fs.removeDirTree(destination)   
            else:
                if o.system.fs.exists(destination):
                    if o.application.shellconfig.interactive:                            
                        if not o.gui.dialog.askYesNo("\nDo you want to overwrite %s" % destination, True):
                            o.gui.dialog.message("Not overwriting %s, it will not be linked" % destination)
                            return        
    
                self._removeDest(destination)
            o.system.fs.symlink(source, destination)        
        
    def _removeDest(self, dest):
        """ Remove a destionation file or directory."""
        isFile = o.system.fs.isFile
        isDir = o.system.fs.isDir
        removeFile = o.system.fs.removeFile
        removeDirTree = o.system.fs.removeDirTree
        exists = o.system.fs.exists

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
    Recipe providing guidelines how to cook a QPackage from source code in
    '''
    def __init__(self):
        self.items = []


    def add(self, coderepoConnection, sourcePath, destinationPath,platform=o.enumerators.PlatformType.GENERIC):
        '''Add a source (ingredient) to the recipe
        '''
        self.items.append(_RecipeItem(coderepoConnection, sourcePath, destinationPath,platform))

    def export(self):
        '''Export all items from VCS to the system sandbox or other location specifed'''
        for item in self.items:
            item.exportToSystem()
            
    def link(self):
        for item in self.items:
            item.linkToSystem()    
            
    def importFromSystem(self,owpackage):
        """
        go from system to files section
        """
        for item in self.items:
            item.importFromSystem(owpackage)                

    def package(self, owpackage, platform):
        # clean up files
        filesPath = owpackage.getPathFiles()        
        o.system.fs.removeDirTree(filesPath)
        
        for item in self.items:
            item.codeToFiles(owpackage, platform)           
        
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

    def identify(self):
        repoconnections = self._getRepoConnections()
        identities = {}
        for repoconnection in repoconnections:
            identity = repoconnection.identify()
            key = repoconnection.repokey
            if not key:
                raise ValueError("Repository %s has no valid repokey" %
                        repoconnection)
            identities[key] = identity

        return identities

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
            if o.system.fs.exists(item.destination):
                return False

        return True

    def removeFromSystem(self):
        '''Remove all folders the recipe has written to'''
        for item in self._items:
            if o.system.fs.isDir(item.destination):
                o.system.fs.removeDirTree(item.destination)
            else:
                o.system.fs.remove(item.destination)

    def __str__(self):
        s="recipe:\n"
        for item in self.items:
            s+="- %s\n" % item
        return s
    
    def __repr__(self):
        return self.__str__()

