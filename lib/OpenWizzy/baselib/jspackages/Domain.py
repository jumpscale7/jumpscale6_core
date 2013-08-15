from OpenWizzy import o

import OpenWizzy.baselib.mercurial

class Domain(): 

    """
    is representation of domain
    source can come from tgz or from mercurial
    """

    def __init__(self, domainname,qualityLevel=None): ## Init must come after definition of lazy getters and setters!
        self.domainname  = domainname
        self.initialized = False
        self._ensureInitialized(qualityLevel)

    def _ensureInitialized(self,qualityLevel=None):

        if self.initialized:
            return
        
        cfgFilePath = o.system.fs.joinPaths(o.dirs.cfgDir, 'owpackages', 'sources.cfg')
        cfg = o.tools.inifile.open(cfgFilePath)

        self.bitbucketreponame=cfg.getValue( self.domainname, 'bitbucketreponame')
        self.bitbucketaccount=cfg.getValue( self.domainname, 'bitbucketaccount')

        if qualityLevel==None:
            self.qualitylevel = cfg.getValue( self.domainname, 'qualitylevel')
        else:
            self.qualitylevel = qualityLevel
        
        self.metadataFromTgz = cfg.getValue(self.domainname, 'metadatafromtgz') in ('1', 'True')        
            
        if self.metadataFromTgz :
            self.metadatadir=o.system.fs.joinPaths(o.dirs.varDir,"owpackages","metadata",self.domainname)
            o.system.fs.createDir(self.metadatadir)
            
        else:
            self._sourcePath = self._getSourcePath()
            self.metadatadir = self.getMetadataDir(self.qualitylevel)
        
        self.blobstorremote=cfg.getValue(self.domainname, 'blobstorremote')
        self.blobstorlocal=cfg.getValue(self.domainname, 'blobstorlocal')
        
        
        
        self.metadataUpload=cfg.getValue(self.domainname, 'metadataupload')
        self.metadataDownload=cfg.getValue(self.domainname, 'metadatadownload')


        self._bitbucketclient = None
        self._mercurialclient = None

        #if not o.system.fs.exists(self.metadatadir):
            #o.console.echo("Could not find owpackage domain %s for quality level %s, will try to get the repo info from tgz or mercurial" % (self.domainname,self.qualitylevel))
            #self.updateMetadata()
            #if not o.system.fs.exists(self.metadatadir):
                #raise RuntimeError("Cannot open owpackage domain %s for quality level %s because path %s does not exist" % (self.domainname,self.qualitylevel,self.metadatadir))
        
        #

        self._metadatadirTmp = o.system.fs.joinPaths(o.dirs.varDir,"tmp","owpackages","md", self.domainname)

        self.initialized = True


    def getQPackageMetadataDir(self, qualitylevel, name, version):
        """
        Get the meta data dir for the Q-Package with `name` and `version` on
        `qualitylevel`.

        @param qualitylevel: quality level
        @type qualitylevel: string
        @param name: name of the Q-Package
        @type name: string
        @param version: version of the Q-Package
        @type version: string
        @return: path of the meta data dir for the Q-Package
        @rtype: string
        """
        metadataDir = self.getMetadataDir(qualitylevel)
        return o.system.fs.joinPaths(metadataDir, name, version)

    def getMetadataDir(self, qualitylevel=None):
        """
        Get the meta data dir for the argument quality level, or for the current
        quality level if no quality level is passed.

        @param qualitylevel: optional quality level to return the metadata dir for
        @type qualitylevel: string
        @return: metadata dir for the argument quality level or the current quality level if no quality level argument is passed
        @rtype: str
        """
        if self.metadataFromTgz:
            raise NotImplementedError("Getting the metadata dir for a tar-gz "
                    "based domain is not yet supported")
        else:
            qualitylevel = qualitylevel or self.qualitylevel
            return o.system.fs.joinPaths(self._sourcePath, qualitylevel)

    def getQualityLevels(self):
        """
        Return the available quality levels for this domain

        @return: the available quality levels for this domain
        @rtype: list(string)
        """
        if self.metadataFromTgz:
            raise NotImplementedError("Getting the quality levels for a tar-gz "
                    "based domain is not yet supported")
        else:
            dirs = o.system.fs.listDirsInDir(self._sourcePath, dirNameOnly=True)
            qualitylevels = [d for d in dirs if not d.startswith('.')]
            return qualitylevels

    def _getSourcePath(self):
        if self.metadataFromTgz:
            raise NotImplementedError("Getting the source path for a tar-gz "
                    "based domain is not yet supported")
        else:
            sourcePath = o.system.fs.joinPaths(o.dirs.codeDir,
                    self.bitbucketaccount, self.bitbucketreponame)
            return sourcePath

    def saveConfig(self):
        """
        Saves changes to the owpackages config file
        """
        cfg = o.tools.inifile.open(o.system.fs.joinPaths(o.dirs.cfgDir, 'owpackages', 'sources.cfg'))
        if not cfg.checkSection(self.domainname):
            cfg.addSection(self.domainname)
        cfg.setParam(self.domainname, 'metadatadownload', self.metadataDownload)
        cfg.setParam(self.domainname, 'metadataupload', self.metadataUpload)
        cfg.setParam(self.domainname, 'metadatafromtgz', int(self.metadataFromTgz))
        cfg.setParam(self.domainname, 'qualitylevel', self.qualitylevel)
        
        #outdated:
        #cfg.setParam(self.domainname, 'metadatabranch', self.metadataBranch)
        #cfg.setParam(self.domainname, 'metadatafrommercurial', self.metadataFromMercurial)

        cfg.write()

    @property
    def bitbucketclient(self):
        if not self._bitbucketclient:
            self._initBitbucketClient()
        return self._bitbucketclient

    @property
    def mercurialclient(self):
        if not self._mercurialclient:
            self._initBitbucketClient()
        return self._mercurialclient

    def _initBitbucketClient(self):
        """
        Ensures we are connected to hg
        Don't do this in the constructor because the mercurial extension may noy yet have been loaded

        """
        self._ensureInitialized()
        if self.metadataFromTgz:
            raise RuntimeError('Meta data is comming from tar, cannot make connection to mercurial server ')

        self._bitbucketclient = o.clients.bitbucket.getBitbucketConnection(self.bitbucketaccount)
        self._mercurialclient = self.bitbucketclient.getMercurialClient(self.bitbucketreponame,branch="default")

    def hasModifiedMetadata(self):
        """
        Checks for the entire domain if it has any modified metadata
        """
        #check mercurial
        if not self.metadataFromTgz:
            return self.mercurialclient.hasModifiedFiles()
        else:
            return False

    def hasModifiedFiles(self): #This is the prepared files?
        """
        Checks for the entire domain if it has any modified files
        """
        for owpackage in self.getQPackages():
            if owpackage.hasModifiedFiles():
                return True
        return False

    def _mercurialLinesToPackageTuples(self, changedFiles):
        changedPackages = set()
        for line in changedFiles: # @todo test on windows
                #  exampleline: zookeeper/1.0/owpackage.cfg
                #  exampleline: zookeeper/1.0/tasklets/sometasklet.py
            line=line.replace("\\","/") #try to get it to work on windows
            splitted=line.split('/')
            if len(splitted)>1:
                name    = splitted[1]
                version = splitted[2]
                owpackage = (self.domainname, name, version)
                changedPackages.add(owpackage)
        return list(changedPackages)

    def getQPackageTuplesWithNewMetadata(self):
        hg = self.bitbucketclient.getMercurialClient(self.bitbucketreponame)
        changedFiles = hg.getModifiedFiles()
        
        #changedFiles = self.hgclient.getModifiedFiles()
        changedFiles = changedFiles["added"] + changedFiles["nottracked"]
        return self._mercurialLinesToPackageTuples(changedFiles)

    def getQPackageTuplesWithModifiedMetadata(self):
        hg = self.bitbucketclient.getMercurialClient(self.bitbucketreponame)
        changedFiles = hg.getModifiedFiles()
        
        #changedFiles = self.hgclient.getModifiedFiles()
        changedFiles = changedFiles["modified"]
        return self._mercurialLinesToPackageTuples(changedFiles)

    def getQPackageTuplesWithDeletedMetadata(self):
        hg = self.bitbucketclient.getMercurialClient(self.bitbucketreponame)
        changedFiles = hg.getModifiedFiles()      
        
        #changedFiles = self.hgclient.getModifiedFiles()
        changedFiles = changedFiles["removed"] + changedFiles['missing']
        return self._mercurialLinesToPackageTuples(changedFiles)

    # Packages that have been deleted will never have modified files
    def getQPackageTuplesWithModifiedFiles(self):
        # Add packages with modified files
        changedQPackages=set()
        for owpackage in self.getQPackages():
            if owpackage.hasModifiedFiles():
                changedQPackages.add((owpackage.domain, owpackage.name, owpackage.version))
        return list(changedQPackages)

    def getModifiedQPackages(self):
        """reloadconfig
        Returns a list with all the packages whose files or metadata have been changed in the currently active domain
        """      
        if self.metadataFromTgz:
            raise RuntimeError("Cannot use modified owpackages from tgz metdata repo")
        changedFiles = self.mercurialclient.getModifiedFiles()
        changedFiles=changedFiles["removed"] + changedFiles['missing']+changedFiles["modified"]+changedFiles["added"] + changedFiles["nottracked"]
        modpackages= self._mercurialLinesToPackageTuples(changedFiles)
        modpackages.extend(self.getQPackageTuplesWithModifiedFiles())
        return modpackages

    def hasDomainChanged(self):
        return self.hasModifiedMetadata() or self.hasModifiedFiles()

    def publishMetadata(self, commitMessage=''): # tars are not uploadable
        """
        Publishes all metadata of the currently active domain
        """
        o.logger.log("Publish metadata for domain %s" % self.domainname,2)
        if not self.metadataFromTgz:
            self.bitbucketclient.push(self.bitbucketreponame, message=commitMessage)
        else:
            raise RuntimeError('Meta data is comming from tar for domain ' + self.domainname + ', cannot publish modified metadata.')


    def publish(self, commitMessage):
        """
        Publishes the currently active domain's bundles & metadata
        
        @debug: It is recommended to NOT use publish() 
                Use a combination of updateMetadata(), publishMetadata() and upload() instead.
                Reason publish() changes the build numbers on top of update()
        """
        o.logger.log("Publish metadata for owpackage domain: %s " % self.domainname ,2)

        # determine which packages changed
        modifiedPackages, mess = self.showChangedItems()
        
        if o.application.shellconfig.interactive:
            if not o.console.askYesNo('continue?'):
                return

        o.logger.log('publishing packages:\n' + mess, 5)

        if not commitMessage:
            commitMessage = o.console.askString('please enter a commit message')

        # If the mercurial source for this domain is not trunck
        # we build the corresponding package for each modified package in the trunck repo
        # We update its buildnumber by two
        # We upload the alternative repo
        # But we don't have the means to do this
        # we should minimize the time to commit, this minimizes the change of concurrent modification errors!
        # This is why bundles are uploaded afterwards
        # @type source DomainSource

        o.logger.log("1) Updating buildNumbers in metadata and uploading files", 1)

        # The build numbers are not modified, but we already committed?
        # How does this work again?
        # Tmp is not updated here?
        # This is actually an update and merge

        self.updateMetadata(commitMessage=commitMessage)  #makes sure metadata from tmp & active repo is updated

        # self._updateMetadataTmpLocation() Where will the tmp repo get updated??

        o.logger.log("2) Updating buildNumbers in metadata and uploading files", 1)
        deletedPackagesMetaData = self.getQPackageTuplesWithDeletedMetadata()
        modifiedPackagesMetaData = self.getQPackageTuplesWithModifiedMetadata()
        modifiedPackagesFiles = self.getQPackageTuplesWithModifiedFiles()
        for owpackageActive in modifiedPackages:
            if owpackageActive in deletedPackagesMetaData:
                o.logger.log("Deleting files of package " + str(owpackageActive), 1)
                o.system.fs.removeDirTree(o.packages.getDataPath(*owpackageActive))
            else:
            #if owpackageActive in newPackagesMetaData or owpackageActive in modifiedPackagesMetaData:
                owpackageActiveObject = o.packages.get(owpackageActive[0], owpackageActive[1], owpackageActive[2])
                o.logger.log("For owpackage: " + str(owpackageActiveObject), 1)
                o.logger.log("current numbers : " + owpackageActiveObject.reportNumbers(), 1)
                # Update build number
                owpackageActiveObject.buildNr  = owpackageActiveObject.buildNr + 1

                # Update meta and bundle number
                if owpackageActive in modifiedPackagesMetaData:
                    owpackageActiveObject.metaNr = owpackageActiveObject.buildNr
                if owpackageActive in modifiedPackagesFiles:
                    owpackageActiveObject.bundleNr = owpackageActiveObject.buildNr
                o.logger.log("updated to new numbers : " + owpackageActiveObject.reportNumbers(), 1)
                owpackageActiveObject.save()

            # At this point we may be
            if owpackageActive in modifiedPackagesFiles:
                owpackageActiveObject = o.packages.get(owpackageActive[0], owpackageActive[1], owpackageActive[2])
                #owpackageActiveObject._compress(overwriteIfExists=True)
                owpackageActiveObject.upload()

        # If we are here and the network drops out
        # What is the result? The tasklets of the last buildNr have changed without incrementing the buildNr
        # Next time we run this the meta data no longer changed and we dont increment the metaNr as a result of it
        #@feedback kristof: this is no issue, above will happen again in next run, the metadata was not uploaded yet so no issue

        o.logger.log("3) Commiting and uploadind metadata with updated buildNumbers", 1)
        self.publishMetadata(commitMessage=commitMessage)

        # Only do this after complete success!
        # If something goes wrong we know which files where modified
        for owpackageActive in modifiedPackagesFiles:
            owpackageActiveObject = o.packages.get(owpackageActive[0], owpackageActive[1], owpackageActive[2])
            owpackageActiveObject._resetPreparedForUpdatingFiles()
    
    
    def showChangedItems(self):    
        """
        Shows all changes in the files or metadata
        """
        o.logger.log("Show changes in files and metadata for owpackage domain: %s " % self.domainname ,2)

        # determine which packages changed
        newPackagesMetaData      = self.getQPackageTuplesWithNewMetadata()
        modifiedPackagesMetaData = self.getQPackageTuplesWithModifiedMetadata() + newPackagesMetaData
        deletedPackagesMetaData  = self.getQPackageTuplesWithDeletedMetadata()
        modifiedPackagesFiles    = self.getQPackageTuplesWithModifiedFiles()
        modifiedPackages         = list(set(newPackagesMetaData + modifiedPackagesMetaData + deletedPackagesMetaData + modifiedPackagesFiles))

        # If there are no packages to do something with don't bother the user
        # with annoying questions
        if not modifiedPackages:
            o.logger.log("There where no modified packages for domain: %s " % self.domainname , 1)
            return modifiedPackages, ''  #debug

        # report to the user what will happen if he proceeds
        o.logger.log('The following packages will be published:', 1)
        just = 15
        mess  = ' ' * 4 + 'domain:'.ljust(just) + 'name:'.ljust(just) + 'version:'.ljust(just)
        mess +=           'metachanged:'.ljust(just) + 'fileschanged:'.ljust(just) + 'status:'.ljust(just) + '\n'
        for package in modifiedPackages:
            metachanged  = package in modifiedPackagesMetaData
            fileschanged = package in modifiedPackagesFiles

            status = 'UNKOWN-ERROR'
            if package in newPackagesMetaData:
                status = 'NEW'
            elif package in modifiedPackagesMetaData:
                status = 'MODIFIED'
            elif package in deletedPackagesMetaData:
                status = 'DELETED'
            elif package in modifiedPackagesFiles:
                status = 'FILES MODIFIED'
            else:
                raise RuntimeError('Unkown status!')

            mess += ' ' * 4 + package[0].ljust(just) + package[1].ljust(just) + package[2].ljust(just)
            mess +=           str(metachanged).ljust(just) + str(fileschanged).ljust(just) + str(status).ljust(just) + '\n'

        o.logger.log('publishing packages for domain %s:\n' % self.domainname + mess, 1)
                    
        return modifiedPackages, mess
    

    def updateMetadata(self, commitMessage="",force=False, accessCode=''):
        """
        Get all metadata of the currently active domain's repo servers and store locally
        
        Depends on the parameter metadataFromTgz.
        Note: Changing the configuration of metadataFromTgz will usually erase 
        the local uncommited modifications of the metadata.
        
        @debug: It is recommended to NOT use publish() 
                Use a combination of updateMetadata(), publishMetadata() and upload() instead.
                Reason publish() changes the build numbers on top of update()
        """
        
        if self.metadataFromTgz == False:

            o.action.start("updateowpackage metadata for domain %s" % self.domainname,\
                           "Could not update the metadata for the domain",\
                           "go to directory %s and update the metadata yourself using mercurial" % self.metadatadir)
                  
            #self.bitbucketclient.checkoutMerge    
            if force:
                self.bitbucketclient.pull(self.bitbucketreponame,update=True,merge=False,checkIgnore=False,force=True)   
            else:
                self.bitbucketclient.pull(self.bitbucketreponame,update=True,merge=True,checkIgnore=False,force=False)   
       
            #link code to right metadata location
            sourcepath = self.getMetadataDir()
            destpath=o.system.fs.joinPaths(o.dirs.packageDir,"metadata",self.domainname)
            o.system.fs.createDir(sourcepath)            
            o.system.fs.symlink(sourcepath,destpath,True)
            
            o.action.stop()
        else:
            repoUrl        = self.metadataDownload
            targetTarDir   = o.packages.getMetaTarPath(self.domainname)
            targetTarFileName = ("metadata_qp5"+'_'+self.domainname+'_'+self.qualitylevel+'.tgz')
            remoteTarPath  = o.system.fs.joinPaths(repoUrl, targetTarFileName)  #@todo P3 needs to work with new tar filenames corresponding to qualitylevels
 
            o.logger.log("Getting meta data from a tar: %s" % remoteTarPath, 1)
            
            if not o.system.fs.exists(targetTarDir):
                o.system.fs.createDir(targetTarDir)
            o.cloud.system.fs.copyFile(remoteTarPath, 'file://' +  targetTarDir) # Add protocol

            ## Extract the tar to the correct location
            if o.system.fs.exists(self.metadatadir):
                o.system.fs.removeDirTree(self.metadatadir)
            targetTarPath = o.system.fs.joinPaths(targetTarDir, targetTarFileName)
            
            o.system.fs.targzUncompress(targetTarPath, self.metadatadir)
            #Note: Syslinks were just overwritten
            
        # Reload all packages
        for package in self.getQPackages():
            package.load()

    def mergeMetadata(self, commitMessage=""):
        """
        #@todo doc
        """
        self._ensureInitialized()
        if not self.metadataFromTgz:
            o.action.start("update & merge owpackage metadata for domain %s" % self.domainname,\
                           "Could not update/merge the metadata for the domain",\
                           "go to directory %s and update/merge/commit the metadata yourself using mercurial" % self.metadatadir)
            hgclient=self.bitbucketclient.getMercurialClient(self.bitbucketreponame)            
            hgclient.pull()
            hgclient.updatemerge(commitMessage=commitMessage,ignorechanges=False,addRemoveUntrackedFiles=True,trymerge=True)	    
            #self.hgclientTmp.pullupdate(commitMessage=commitMessage) ? not needed no?
            o.action.stop()
        else:
            raise RuntimeError("Cannot merge metadata from tgz info, make sure in sources.cfg file this domain %s metadata is not coming from a tgz file"% self.domainname)

        # Reload all packages
        for package in self.getQPackages():
            package.reload()	    

    def publishMetaDataAsTarGz(self):
        
        #self._ensureInitialized()
        revisionTxt = o.system.fs.joinPaths(self.metadatadir, 'revision.txt')
        
        if self.metadataFromTgz == False:
            hg = self.bitbucketclient.getMercurialClient(self.bitbucketreponame)
            id = hg.id()            
            o.system.fs.writeFile(revisionTxt, id) #this to remember from which revision the tgz has been created
            
        targetTarDir  = o.packages.getMetaTarPath(self.domainname)
        targetTarFileName = ("metadata_qp5"+'_'+self.domainname+'_'+self.qualitylevel+'.tgz')
        targetTarPath = o.system.fs.joinPaths(targetTarDir, targetTarFileName)
        
        o.logger.log("Building tar file from " + self.metadatadir + " to location " + targetTarPath)

        o.system.fs.targzCompress(self.metadatadir, targetTarPath, pathRegexExcludes=['.*\/\.hg\/.*'])
        
        o.system.fs.removeFile(revisionTxt)    
        
        remoteTarDir  = self.metadataUpload
        o.logger.log("Uploading tar file for owpackage metadata" + targetTarPath + " to location " + remoteTarDir)
        o.cloud.system.fs.copyFile('file://' +  targetTarPath, 'file://' +  remoteTarDir + "/")        
        o.system.fs.removeFile(targetTarPath)
    

    def _isTrackingFile(self, file):
        # test if the file is commited
        file.replace(self.metadatadir,"")
        if file[0]=="/":
            file=file[1:]
        curpath=o.system.fs.getcwd()
        o.system.fs.changeDir(self.metadatadir)
        hgclient=self.bitbucketclient.getMercurialClient(self.bitbucketreponame)
        result=hgclient.isTrackingFile(file)
        o.system.fs.changeDir(curpath)
        return result

    def getLatestBuildNrForQPackage(self,domain,name,version):
        """
        Returns the lastest buildnumber
        Buildnr comes from default tip of mercurial repo
        """        
        owpackage=o.packages.get(domain,name,version,"default",fromTmp=True)
        return owpackage.buildNr

    def getQPackages(self):
        """
        Returns a list of all owpackages of the currently active domain
        """
        return o.packages.find(domain=self.domainname)
    
    
    def switchQualityLevel(self, qlevel):
        '''
        Allows a clean reconfiguration for a new quality level, and be sure that the configurations are OK.
        All packages are reinstalled, if need.
        NO active removal of unneeded packages.
        Includes a check that the repository has the new quality level
        '''
                  
        o.console.echo("\nDomain:  %s\n %s (Repo)\n %s (Quality Level)\n %s (MetaFromTgz)\n" % (self.domainname,self.bitbucketreponame,self.qualitylevel,self.metadataFromTgz))
        self.updateMetadata()
        
        #check that new quality level is valid in this metadata repo
        list=[]
        list = o.system.fs.listDirsInDir(path=self._sourcepath, dirNameOnly=True)
        if qlevel in list:
            o.console.echo("Found matching Quality Level in repo. - %s - has quality level: %s" % (self.domainname, qlevel))
        else:
            raise RuntimeError("Metadata repo %s of domain %s has no such Quality Level %s " % (self.bitbucketreponame, self.domainname, qlevel))
        
        self._ensureInitialized()
        QLFrom = self.qualitylevel
        
        self.qualitylevel = qlevel
        self.saveConfig()
        
        self._ensureInitialized()
        QLTo = self.qualitylevel
        o.console.echo("Changed quality level of domain %s from: %s to: %s " % (self.domainname,QLFrom, QLTo))
        
        #reinstall all packages of domain, if needed       
        for package in self.getQPackages():
            package.reload()
            o.console.echo("%s %s" % (package.name, package.version))
            
            #find at least one platform with a checksum
            matchOne = False
            for platform in package.supportedPlatforms:
                c = package.getChecksum(platform)
                if c <> None:
                    o.console.echo("    %s %s " % (platform, c))
                    matchOne = True
            
            if matchOne == True:
                package.install(dependencies=False, reinstall=True, download=True)
                o.console.echo("\n    >>>> Successful Download")
            else: 
                o.console.echo("    No checksum for any platform of this package/version.")
        
        self.updateMetadata()  #importantly, this resets the symlink to the metadata directories
                
        return 0
        
    def __str__(self):
        self._ensureInitialized()
        return "domain:%s\nmetadataDownload:%s\nmetadataUpload:%s\nqualitylevel:%s\nmetadataFromTgz:%s\n" % \
               (self.domainname,self.metadataDownload,self.metadataUpload,self.qualitylevel,self.metadataFromTgz)

    def __repr__(self):
        return self.__str__()

    def _ensureDomainCanBeUpdated(self):
        if self.metadataFromTgz:
            raise RuntimeError('For domain: ' + self.domainname + ': Meta data comes from tgz, cannot update domain.')
        if self.metadataUpload == None:
            raise RuntimeError('For domain: ' + self.domainname + ': Not metadataUpload location specified, cannot update domain.')
