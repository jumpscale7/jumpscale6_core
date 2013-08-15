import math
from OpenWizzy import o
from QPackageObject4 import QPackageObject4
from Domain import Domain
from CodeManagementRecipe import CodeManagementRecipe
from OpenWizzy.core.enumerators.PlatformType import PlatformType

class QPackageClient4():
    sourcesFile = None

    """
    methods to deal with owpackages, seen from client level

    @qlocation o.packages
    """
    def __init__(self):
        """
        """
        o.system.fs.createDir(o.system.fs.joinPaths(o.dirs.packageDir, "metadata"))
        o.system.fs.createDir(o.system.fs.joinPaths(o.dirs.packageDir, "files"))
        o.system.fs.createDir(o.system.fs.joinPaths(o.dirs.packageDir, "bundles"))
        o.system.fs.createDir(o.system.fs.joinPaths(o.dirs.packageDir, "metatars"))
        self.domains=[]
        self._metadatadirTmp=o.system.fs.joinPaths(o.dirs.varDir,"tmp","owpackages","md")
        o.system.fs.createDir(self._metadatadirTmp)        
        # can't ask username here
        # because openwizzy is not interactive yet
        # So we ask the username/passwd lazy in the domain object
        self.reloadconfig()
        self.resetState()

    def getQPackageMetadataScanner(self):
        """
        returns tool which can be  used to scan the owpackage repo's and manipulate them
        """
        
        from core.owpackages6.QPackageMetadataScanner import QPackageMetadataScanner
        return QPackageMetadataScanner()

    def _renew(self):
        o.packages = QPackageClient6()

    def checkProtectedDirs(self,redo=True,checkInteractive=True):
        """
        recreate the config file for protected dirs (means directories linked to code repo's)
        by executing this command you are sure that no development data will be overwritten
        @param redo means, restart from existing links in qbase, do not use the config file
        @checkInteractive if False, will not ask just execute on it
        """
     
        result,llist=o.system.process.execute("find /opt/qbase5 -type l")
        lines=[item for item in llist.split("\n") if item.strip()<>""]
        if len(lines)>0:
            cfgpath=o.system.fs.joinPaths(o.dirs.cfgDir,"debug","protecteddirs","protected.cfg")
            if redo==False and o.system.fs.exists(cfgpath):
                llist=o.system.fs.fileGetContents(cfgpath)
                lines.extend([item for item in llist.split("\n") if item.strip()<>""])
            prev=""
            lines2=[]
            lines.sort()
            for line in lines:
                if line<>prev:
                    lines2.append(line)
                prev=line
            out="\n".join(lines2)
            do=False
            if checkInteractive: 
                if o.console.askYesNo("Do you want to make sure that existing linked dirs are not overwritten by installer? \n(if yes the linked dirs will be put in protected dir configuration)\n"):
                    do=True
            else:
                do=True
            if do:
                o.system.fs.writeFile(cfgpath,out)     

    def reloadconfig(self):
        """
        Reload all owpackage config data from disk
        """
        self.resetState()
        cfgpath=o.system.fs.joinPaths(o.dirs.cfgDir, 'owpackages6', 'sources.cfg')

        if not o.system.fs.exists(cfgpath):
            #check if there is old owpackage dir
            cfgpathOld=o.system.fs.joinPaths(o.dirs.cfgDir, 'owpackages5', 'sources.cfg')            
            if o.system.fs.exists(cfgpathOld):
                o.system.fs.renameDir(o.system.fs.joinPaths(o.dirs.cfgDir, 'owpackages5'),o.system.fs.joinPaths(o.dirs.cfgDir, 'owpackages6'))

        if not o.system.fs.exists(cfgpath):
            o.system.fs.createDir(o.system.fs.getDirName(cfgpath))
        else:
            cfg = o.tools.inifile.open(cfgpath)
            self.sourcesConfig=cfg
            domainDict = dict()
            for domains in self.domains: 
                domainDict[domains.domainname] = domains
            for domain in cfg.getSections():
                if domain in domainDict.keys():
                    self.domains.remove(domainDict[domain])
                self.domains.append(Domain(domainname=domain))


    def createNewQPackage(self, domain, name, version="1.0", description="", supportedPlatforms=[o.enumerators.PlatformType.LINUX]):
        """
        Creates a new owpackage4, this includes all standard tasklets, a config file and a description.wiki file
        @param domain:      string - The domain the new owpackage should reside in
        @param name:        string - The name of the new owpackage
        @param version:     string - The version of the new owpackage
        @param description: string - The description of the new owpackage (is stored in the description.wiki file)
        @param supportedPlatforms  [o.enumerators.PlatformType.LINUX,...] other examples WIN,LINUX32,LINUX64
        """
        supportedPlatforms=[str(item) for item in supportedPlatforms]
        # Create one in the repo
        if not domain in o.packages.getDomainNames():
            raise RuntimeError('Provided domain is nonexistent on this system')
        if self.getDomainObject(domain).metadataFromTgz:
            raise RuntimeError('The meta data for domain ' + domain + ' is coming from a tgz, you cannot create new packages in it.')
        qp      = QPackageObject4(domain, name, version)
        #qp.prepareForUpdatingFiles(suppressErrors=True)
        qp.supportedPlatforms = supportedPlatforms
        qp.description=description
        qp.save()
        o.system.fs.createDir(qp.getPathFiles())
        o.system.fs.createDir(o.system.fs.joinPaths(qp.getPathFiles(),"generic"))
        for pl in supportedPlatforms:
            o.system.fs.createDir(o.system.fs.joinPaths(qp.getPathFiles(),"%s"%pl))
        return qp


############################################################
##################  GET FUNCTIONS  #########################
############################################################

    def getCodeManagementRecipe(self):
        return CodeManagementRecipe()

    def get(self, domain, name, version):
        """
        Returns a owpackage 
        @param domain:  string - The domain the owpackage is part from
        @param name:    string - The name of the owpackage
        @param version: string - The version of the owpackage
        """
        # return a package from the default repo
        key = '%s%s%s' % (domain,name,version)
        if self._getcache.has_key(key):
            return self._getcache[key]
        if self.exists(domain,name,version)==False:
            raise RuntimeError("Could not find package %s." % self.getMetadataPath(domain,name,version))
        self._getcache[key]=QPackageObject4(domain, name, version)
        return self._getcache[key]

    def downloadAllBundles(self,die=True):
        """
        Downloads all bundles from all packages in all domains from the repos
        """
        for package in self.getQPackageObjects():
            if die==False:
                try:
                    package.download(allplatforms=True)
                except:
                    o.console.echo("could not download package %s" % package.name)
            else:
                package.download()
                    
                
    def copyAllBundlesToNewStorageLocation(self,path,die=True,appendDescr=True):
        for package in self.getQPackageObjects():
            package.copyBundleToNewStorageLocation(path,die=die,appendDescr=appendDescr)

    def exists(self,domain,name,version):
        """
        Checks whether the owpackage's metadata path is currently present on your system
        """
        return o.system.fs.exists(self.getMetadataPath(domain,name,version))

    def getInstalledPackages(self):
        """
        Returns a list of all currently installed packages on your system
        """
        return [p for p in self.getQPackageObjects() if p.isInstalled()]

    def getPackagesWithBrokenDependencies(self):
        """
        Returns a list of all owpackages which have dependencies that cannot be resolved
        """
        return [package for package in self.getQPackageObjects() if len(package.getBrokenDependencies()) > 0]
    
    def getPendingReconfigurationPackages(self):
        """
        Returns a List of all owpackages that are pending for configuration
        """
        return filter(lambda owpackage: owpackage.isPendingReconfiguration(), self.getQPackageObjects())

#############################################################
######################  DOMAINS  ############################
#############################################################

    def getDomainObject(self,domain,qualityLevel=None):
        """
        Get provided domain as an object
        """
        if qualityLevel==None:
            for item in self.domains:
                if item.domainname.lower()==domain.lower().strip():
                    return item
        else:
            return Domain(domain,qualityLevel)
        
        raise RuntimeError("Could not find owpackage domain %s" % domain)

    def getDomainNames(self):
        """
        Returns a list of all domains present in the sources.cfg file
        """
        result=[]
        for item in self.domains:
            result.append(item.domainname)
        return result


############################################################
###################  GET PATH FUNCTIONS  ###################
############################################################

    def getQPActionsPath(self,domain,name,version,fromtmp=False):
        """
        Returns the metadatapath for the provided owpackage
        if fromtmp is True, then tmp directorypath will be returned

        @param domain:  string - The domain of the owpackage
        @param name:    string - The name of the owpackage
        @param version: string - The version of the owpackage
        @param fromtmp: boolean
        """
        if fromtmp:
            self._metadatadirTmp
            return o.system.fs.joinPaths(self._metadatadirTmp,domain,name,version,"actions")
        else:
            return o.system.fs.joinPaths(o.dirs.packageDir, "active", domain,name,version,"actions")


    def getQPActiveHRDPath(self,domain,name,version,fromtmp=False):
        """
        Returns the metadatapath for the provided owpackage
        if fromtmp is True, then tmp directorypath will be returned

        @param domain:  string - The domain of the owpackage
        @param name:    string - The name of the owpackage
        @param version: string - The version of the owpackage
        @param fromtmp: boolean
        """
        if fromtmp:
            self._metadatadirTmp
            return o.system.fs.joinPaths(self._metadatadirTmp,domain,name,version,"hrd")
        else:
            return o.system.fs.joinPaths(o.dirs.packageDir, "active", domain,name,version,"hrd")

    def getMetadataPath(self,domain,name,version):
        """
        Returns the metadatapath for the provided owpackage for active state

        @param domain:  string - The domain of the owpackage
        @param name:    string - The name of the owpackage
        @param version: string - The version of the owpackage
        @param fromtmp: boolean
        """
        return o.system.fs.joinPaths(o.dirs.packageDir, "metadata", domain,name,version)

    def getDataPath(self,domain,name,version):
        """
        Returns the filesdatapath for the provided owpackage
        @param domain:  string - The domain of the owpackage
        @param name:    string - The name of the owpackage
        @param version: string - The version of the owpackage
        """
        return o.system.fs.joinPaths(o.dirs.packageDir, "files", domain,name,version)

    def getMetaTarPath(self, domainName):
        """
        Returns the metatarsdatapath for the provided domain
        This is the place where the .tgz bundles are stored for each domain
        """
        return o.system.fs.joinPaths(o.dirs.packageDir, "metatars", domainName)

    # This is a name inconsitency with owpackage.getPathFiles
    #                                          .getPathBundles
    # Put Path in front or in back, but not both?
    def getBundlesPath(self):
        """
        Returns the bundlesdatapath where all bundles are stored for all different domains
        """
        return o.system.fs.joinPaths(o.dirs.packageDir, "bundles")


############################################################
######################  CACHING  ###########################
############################################################

    _getcache = {}

    def _deleteFromCache(self, domain, name, version):
        #called by a package when we call delete on it so it can be garbage collected
        key = '%s%s%s' % (domain, name, version)
        self._getcache.remove(key)



############################################################
##########################  FIND  ##########################
############################################################

    def findNewest(self, name="", domain="", minversion="",maxversion="",platform=o.enumerators.PlatformType.GENERIC, returnNoneIfNotFound=False):
        """
        Find the newest owpackage which matches the criteria
        If more than 1 owpackage matches -> error
        If no owpackage match and not returnNoneIfNotFound -> error
        @param name:       string - The name of owpackage you are looking for
        @param domain:     string - The domain of the owpackage you are looking for
        @param minversion: string - The minimum version the owpackage must have
        @param maxversion: string - The maximum version the owpackage can have
        @param platform:   string - Which platform the owpackage must run on
        @param returnNoneIfNotFound: boolean - if true, will return None object if no owpackages have been found
        """
        results=self.find(domain=domain,name=name,platform=platform)
        namefound=""
        domainfound=""
        if minversion=="":
            minversion="0"
        if maxversion=="":
            maxversion="100.100.100"
        #look for duplicates
        for qp in results:
            if namefound=="":
                namefound=qp.name
            if domainfound=="":
                domainfound=qp.domain
            if qp.domain<>domainfound or qp.name<>namefound:
                packagesStr="\n"
                for qp2 in results:
                    packagesStr="    %s\n" % str(qp2)
                raise RuntimeError("Found more than 1 owpackage matching the criteria.\n %s" % packagesStr)
        #check for version match
        if len(results)==0:
            if returnNoneIfNotFound:
                return None
            raise RuntimeError("Did not find owpackage with criteria domain:%s, name:%s, platform:%s (independant from version)" % (domain,name,platform))
        # filter packages so they ly between min and max version bounds
        result=[qp for qp in results if self._getVersionAsInt(minversion)<=self._getVersionAsInt(qp.version)<=self._getVersionAsInt(maxversion)]
        result.sort(lambda qp1, qp2: - int(self._getVersionAsInt(qp1.version) - self._getVersionAsInt(qp2.version)))
        if not result:
            if returnNoneIfNotFound:
                return None
            raise RuntimeError("Did not find owpackage with criteria domain:%s, name:%s, minversion:%s, maxversion:%s, platform:%s" % (domain,name,minversion,maxversion,platform))
        return result[0]

    def find(self, name="", domain="", version="", platform=o.enumerators.PlatformType.GENERIC):
        """
        returns list of found owpackages
        @param domain:  string - The name of owpackage domain, when using * means partial name
        @param name:    string - The name of the owpackage you are looking for
        @param version: string - The version of the owpackage you are looking for
        """
        o.logger.log("Find owpackage domain:%s name:%s version:%s platform:%s" %(domain,name,version,platform))
        #work with some functional methods works faster than doing the check everytime
        def findPartial(pattern,text):
            pattern=pattern.replace("*","")
            if text.lower().find(pattern.lower().strip())<>-1:
                return True
            return False

        def findFull(pattern,text):
            return pattern.strip().lower()==text.strip().lower()

        def alwaysReturnTrue(pattern,text):
            return True

        domainFindMethod=alwaysReturnTrue
        nameFindMethod=alwaysReturnTrue
        versionFindMethod=alwaysReturnTrue

        if domain:
            if domain.find("*")<>-1:
                domainFindMethod=findPartial
            else:
                domainFindMethod=findFull
        if name:
            if name.find("*")<>-1:
                nameFindMethod=findPartial
            else:
                nameFindMethod=findFull
        if version:
            if version.find("*")<>-1:
                versionFindMethod=findPartial
            else:
                versionFindMethod=findFull
        result=[]
        for p_domain, p_name, p_version in self._getQPackageTuples():
            if domainFindMethod(domain,p_domain) and nameFindMethod(name,p_name) and versionFindMethod(version,p_version):
                result.append([p_domain, p_name, p_version])
        result2=[]
        for item in result:
                result2.append(self.get(item[0],item[1], item[2]))
        return result2

    # Used in getQPackageObjects and that is use in find
    def _getQPackageTuples(self):
        res = list()
        domains=self.getDomainNames()
        for domainName in domains:
            domainpath=o.system.fs.joinPaths(o.dirs.packageDir, "metadata", domainName)
            if o.system.fs.exists(domainpath): #this follows the link
                packages= [p for p in o.system.fs.listDirsInDir(domainpath,dirNameOnly=True) if p != '.hg'] # skip hg file
                for packagename in packages:
                    packagepath=o.system.fs.joinPaths(domainpath,packagename)
                    versions=o.system.fs.listDirsInDir(packagepath,dirNameOnly=True)
                    for version in versions:
                        res.append([domainName,packagename,version])
        return res

    def getQPackageObjects(self, platform=o.enumerators.PlatformType.GENERIC, domain=None):
        """
        Returns a list of owpackage objects for specified platform & domain
        """
        def hasPlatform(package):
            return any([supported.has_parent(platform) for supported in package.supportedPlatforms])
        packageObjects = [self.get(*p) for p in self._getQPackageTuples()]
        return [p for p in packageObjects if hasPlatform(p) and (domain == None or p.domain == domain)]


############################################################
########  CHECK ON ALREADY EXECUTED ACTIONS  ###############
############################################################

    def _actionGetName(self,owpackageObject,action):
        return "%s_%s_%s_%s" % (\
                    owpackageObject.domain,owpackageObject.name,owpackageObject.version,action)        

    def resetState(self):
        """
        make sure that previous actions on owpackages are not remembered, re-execute all actions
        """
        self._activeActions={}

    def _actionCheck(self,owpackageObject,action):
        """
        check if that action has already been executed if yes return true
        """
        return self._activeActions.has_key(self._actionGetName(owpackageObject,action))

    def _actionSet(self,owpackageObject,action):
        """
        set that the action has already been executed
        """
        self._activeActions[self._actionGetName(owpackageObject,action)]=True


############################################################
#################  UPDATE / PUBLISH  #######################
############################################################

    def init(self):
        pass

    def updateMetaData(self,domain="",force=False):
        """
        Does an update of the meta information repo for each domain
        """
        self.resetState()
        if domain<>"":
            o.logger.log("Update metadata information for owpackages domain %s" % domain, 1)
            d=self.getDomainObject(domain)
            d.updateMetadata(force=force)
        else:
            if o.application.shellconfig.interactive:
                domainnames=o.console.askChoiceMultiple(o.packages.getDomainNames())
            else:
                domainnames=self.getDomainNames()            
            for domainName in domainnames:
                self.updateMetaData(domainName, force=force)

    def mergeMetaData(self,domain="", commitMessage=''):
        """
        Does an update of the meta information repo for each domain
        """

        if not o.application.shellconfig.interactive:
            if commitMessage == '':
                raise RuntimeError('Need commit message')

        if domain<>"":
            o.logger.log("Merge metadata information for owpackages domain %s" % domain, 1)
            d=self.getDomainObject(domain)
            d.mergeMetadata(commitMessage=commitMessage)
        else:
            for domainName in self.getDomainNames():
                self.mergeMetaData(domainName, commitMessage=commitMessage)

    def _getQualityLevels(self,domain):
        cfg=self.sourcesConfig        
        bitbucketreponame=cfg.getValue( domain, 'bitbucketreponame')
        bitbucketaccount=cfg.getValue( domain, 'bitbucketaccount')      
        qualityLevels=o.system.fs.listDirsInDir(o.system.fs.joinPaths(o.dirs.codeDir,bitbucketaccount,bitbucketreponame),dirNameOnly=True)        
        qualityLevels=[item for item in qualityLevels if item<>".hg"]
        return qualityLevels
    
    def _getMetadataDir(self,domain,qualityLevel=None,descr=""):
        cfg=self.sourcesConfig        
        bitbucketreponame=cfg.getValue( domain, 'bitbucketreponame')
        bitbucketaccount=cfg.getValue( domain, 'bitbucketaccount')      
        if descr=="":
            descr="please select your qualitylevel"
        if qualityLevel==None or qualityLevel=="":
            qualityLevel=o.console.askChoice(self._getQualityLevels(domain),descr)
        return o.system.fs.joinPaths(o.dirs.codeDir,bitbucketaccount,bitbucketreponame,qualityLevel)      

    def metadataDeleteQualityLevel(self, domain="",qualityLevel=None):
        """
        Delete a quality level 
        """
        if domain<>"":
            o.logger.log("Delete quality level %s for %s." % (qualityLevel,domain), 1)
            metadataPath=self._getMetadataDir(domain,qualityLevel)            
            o.system.fs.removeDirTree(metadataPath)
        else:
            if o.application.shellconfig.interactive:
                domainnames=o.console.askChoiceMultiple(o.packages.getDomainNames())
            else:
                domainnames=self.getDomainNames()
            for domainName in domainnames:
                self.metadataDeleteQualityLevel(domainName,qualityLevel)


    def metadataCreateQualityLevel(self, domain="",qualityLevelFrom=None,qualityLevelTo=None,force=False,link=True):
        """
        Create a quality level starting from the qualitylevelFrom e.g. unstable to beta
        @param link if True will link the owpackages otherwise copy
        @param force, will delete the destination
        """
        if domain<>"":
            o.logger.log("Create quality level for %s from %s to %s" % (domain,qualityLevelFrom,qualityLevelTo), 1)
            metadataFrom=self._getMetadataDir(domain,qualityLevelFrom,"please select your qualitylevel where you want to copy from for domain %s." % domain)
            if qualityLevelTo==None or qualityLevelTo=="":
                qualityLevelTo=o.console.askString("Please specify qualitylevel you would like to create for domain %s" % domain)                
            metadataTo=self._getMetadataDir(domain,qualityLevelTo)
            dirsfrom=o.system.fs.listDirsInDir(metadataFrom)
            if o.system.fs.exists(metadataTo):
                if force or o.console.askYesNo("metadata dir %s exists, ok to remove?" % metadataTo):
                    o.system.fs.removeDirTree(metadataTo)
                else:
                    raise RuntimeError("Cannot continue to create metadata for new qualitylevel, because dest dir exists")
            o.system.fs.createDir(metadataTo)
            for item in dirsfrom:
                while o.system.fs.isLink(item):
                    #look for source of link                
                    item=o.system.fs.readlink(item)
                dirname=o.system.fs.getDirName( item+"/", lastOnly=True)
                if link:
                    o.system.fs.symlink( item,o.system.fs.joinPaths(metadataTo,dirname),overwriteTarget=True)
                else:
                    o.system.fs.copyDirTree(item, o.system.fs.joinPaths(metadataTo,dirname), keepsymlinks=False, eraseDestination=True)
        else:
            if o.application.shellconfig.interactive:
                domainnames=o.console.askChoiceMultiple(o.packages.getDomainNames())
            else:
                domainnames=self.getDomainNames()
            for domainName in domainnames:
                self.metadataCreateQualityLevel(domainName,qualityLevelFrom,qualityLevelTo,force,link)

                
   
    def publishMetaDataAsTarGz(self, domain="",qualityLevel=None):
        """
        Updates the metadata for all domains (if no domain specified), makes a tar from it and uploads the tar to the owpackage server so tar based clients can now use the latest packages
        """
        if domain<>"":
            o.logger.log("Push metadata information for owpackages domain %s to reposerver." % domain, 1)
            if qualityLevel=="all":
                for ql in self._getQualityLevels(domain):
                    d = self.getDomainObject(domain,qualityLevel=ql)
                    d.publishMetaDataAsTarGz()                
            else:
                d = self.getDomainObject(domain,qualityLevel=qualityLevel)
                d.publishMetaDataAsTarGz()
           
        else:
            if o.application.shellconfig.interactive:
                domainnames=o.console.askChoiceMultiple(o.packages.getDomainNames())
            else:
                domainnames=self.getDomainNames()
            for domainName in domainnames:
                self.publishMetaDataAsTarGz(domainName,qualityLevel=qualityLevel)

    def publish(self, commitMessage,domain=""):
        """
        Publishes all domains' bundles & metadata (if no domain specified)
        @param commitMessage: string - The commit message you want to assign to the publish
        """
        if domain=="":
            for domain in o.packages.getDomainNames():
                self.publish( commitMessage=commitMessage,domain=domain)
        else:
            domainobject=o.packages.getDomainObject(domain)
            domainobject.publish(commitMessage=commitMessage)


##########################################################
####################  RECONFIGURE  #######################
##########################################################

    def _setHasPackagesPendingConfiguration(self, value=True):
        file = o.system.fs.joinPaths(o.dirs.baseDir, 'cfg', 'owpackages6', 'reconfigure.cfg')
        if not o.system.fs.exists(file):
            ini_file = o.tools.inifile.new(file)
        else:
            ini_file = o.tools.inifile.open(file)

        if not ini_file.checkSection('main'):
            ini_file.addSection('main')


        ini_file.setParam("main","hasPackagesPendingConfiguration", "1" if value else "0")
        ini_file.write()

    def _hasPackagesPendingConfiguration(self):
        file = o.system.fs.joinPaths(o.dirs.baseDir, 'cfg', 'owpackages6', 'reconfigure.cfg')
        if not o.system.fs.exists(file):
            return False
        ini_file = o.tools.inifile.open(file)

        if ini_file.checkSection('main'):
            return ini_file.getValue("main","hasPackagesPendingConfiguration") == '1'

        return False

    def _runPendingReconfigeFiles(self):
        if not self._hasPackagesPendingConfiguration():
            return

        # Get all packages that need reconfiguring and reconfigure them
        # We store the state to reconfigure them in their state files
        configuredPackages = set()
        currentPlatform = PlatformType.findPlatformType()

        def configure(package):
            # If already processed return
            if package in configuredPackages:
                return True
            configuredPackages.add(package)

            # first make sure depending packages are configured
            for dp in package.getDependencies(recursive=False, platform=currentPlatform):
                if not configure(dp):
                    return False

            # now configure the package
            if package.isPendingReconfiguration():
                o.logger.log("owpackage %s %s %s needs reconfiguration" % (package.domain,package.name,package.version),3)
                try:
                    package.configure()
                except:
                    q.debugging.printTraceBack('Got error while reconfiguring ' + str(package))
                    if o.console.askChoice(['Skip this one', 'Go to shell'], 'What do you want to do?') == 'Skip this one':
                        return True
                    else:
                        return False
            return True


        pendingPackages = self.getPendingReconfigurationPackages()
        hasPendingConfiguration = False
        for p in pendingPackages:
            if not configure(p):
                hasPendingConfiguration = True
                break

        self._setHasPackagesPendingConfiguration(hasPendingConfiguration)


############################################################
################  SUPPORTING FUNCTIONS  ####################
############################################################

    def _getVersionAsInt(self,version):
        """
        @param version is string
        """
        if version.find(",")<>-1:
            raise RuntimeError("version string can only contain numbers and . e.g. 1.1.1")
        if version=="":
            version="0"
        if version.find(".")<>-1:
            versions=version.split(".")
        else:
            versions=[version]
        if len(versions)>4:
            raise RuntimeError("max level of versionlevels = 4 e.g. max 1.1.1.1")
        #make sure always 4 levels of versions for comparison
        while(len(versions)<4):
            versions.append("0")
        result=0
        for counter in range(0,len(versions)):
            level=len(versions)-counter-1
            if versions[counter]=="":
                versions[counter]="0"
            result=int(result+(math.pow(1000,level)*int(versions[counter].strip())))
        return result

    def pm_getQPackageConfig(self, owpackageMDPath):
        return QPackageConfig(owpackageMDPath)

    def makeDependencyGraph(self):
        '''
        Creates a graphical visualization of all dependencies between the QPackackages of all domains.
        This helps to quickly view and debug the dependencies and avoid errors.
        The target audience are the developers of accross groups and domains that depend on each others packages.
        
        The graph can be found here:   
        /opt/qbase5/var/owpackages6/metadata/dependencyGraph.png
        
        Notes:  
        The graph omits the constraints, such as version numbers and platform.
        
        For completeness, a second graph is created that shows packages without andy dependencies (both ways). 
        See: dependencyGraph_singleNodes.png
        '''

        from pygraphviz import AGraph  #import only here to avoid overhead
        
        def _getPackageTagName(obj, separator=' - '):
            n = obj.name
            #n += '\\n'
            #n  += obj.domain
            return n

        o.console.echo("Making Dependency graph ... please wait.")
    
        platform = PlatformType.getByName('generic')
           
        g=AGraph(strict=True,directed=True, compound=True)
        
        g.graph_attr['rankdir']='LR'
        g.graph_attr['ratio']=1.3
    
        #Generate the graph
        for pack in o.packages.getQPackageObjects():
            dn= 'cluster_'+pack.domain
            s= g.add_subgraph(name = dn)
            s.add_node(_getPackageTagName(pack))
            
            x=g.get_node(_getPackageTagName(pack))
            x.attr['label']=_getPackageTagName(pack)
            
            depList= pack.getDependencies(platform, recursive=False)
            for dep in depList:
                g.add_node(_getPackageTagName(dep))
                g.add_edge(_getPackageTagName(pack),_getPackageTagName(dep))
       
        #Separate nodes with and without links
        singleNodes=[]
        linkedNodes=[]
        for n in g.nodes():
            c=[]
            c=g.neighbors(n)
            if c==[]:
                singleNodes.append(n)
            else:
                linkedNodes.append(n)
     
        #Add the domain name to the graph
        for pack in o.packages.getQPackageObjects():
            n=pack.domain
            dn= 'cluster_'+pack.domain       
    
            s= g.add_subgraph(name=dn)
            s.add_node(n)
                        
            x=g.get_node(n)
            x.attr['label']=n
            x.attr['style']='filled'
            x.attr['shape']='box'
            
        #Create a second version, for the graph of single nodes
        stemp=g.to_string()        
        s=AGraph(stemp)    
        
        for n in singleNodes:
            g.delete_node(n)
    
        for n in linkedNodes:
            s.delete_node(n)
        
        g.layout(prog='dot')    
        graphPath = o.system.fs.joinPaths(o.dirs.packageDir, 'metadata','dependencyGraph.png')
        g.draw(graphPath)
    
        s.layout(prog='dot')
        graphPath = o.system.fs.joinPaths(o.dirs.packageDir, 'metadata','dependencyGraph_singleNodes.png')
        s.draw(graphPath)

        o.console.echo("Dependency graph successfully created. Open file at /opt/qbase5/var/owpackages6/metadata/dependencyGraph.png")
