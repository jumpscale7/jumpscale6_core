from OpenWizzy import o
import collections
import imp
import random
import sys

def monkey_getRepoConnection(accountName, repoName, branch='default'):
    #return 'https://bitbucket.org/%s/%s/ %s/%s %s' % (accountName, repoName, o.dirs.codeDir, repoName, branch)
    return [accountName,repoName,branch]        

class DuplicateFilesResult(object):
    """Helper class that can print a dict of duplicate file information in
    multiple interesting ways"""

    def __init__(self, perFileDict):
        self.perFileDict = perFileDict

    def echoDuplicatesByPackage(self):
        """
        Echo the duplicate files, grouped by the packages they are in
        """
        def prettyPackages(packages):
            def prettyPackage(p):
                return p.path
            return "\n".join(["Duplicate files for:"] + [prettyPackage(p) for p in packages])

        # I am misusing the pretty-printed packages as a unique key in a dict.
        # That way file paths are grouped by the packages that contain those
        # paths.
        invertedDups = collections.defaultdict(list)
        for filePath, packages in self.perFileDict.iteritems():
            if len(packages) > 1:
                invertedDups[prettyPackages(packages)].append(filePath)

        echo = o.console.echo
        for d, filePaths in invertedDups.iteritems():
            echo(d)
            for filePath in sorted(filePaths):
                echo(filePath, indent=4)
            echo("\n")

    def echoDuplicatesByFile(self):
        """
        Echo the duplicate files, per file
        """
        for filePath, packages in self.perFileDict.iteritems():
            if len(packages) > 1:
                o.console.echo("%s" % filePath)
                o.console.echo("Available in:")
                for qp in packages:
                    name = "%s %s %s %s" % (qp.qualitylevel, qp.domain,
                            qp.name, qp.version)
                    o.console.echo(name, indent=4)
                o.console.echo("")


class QPModel():
    """
    this is a data model for owpackages which can be  used to manipulate the repo
    """
    def __init__(self, qualitylevel, name, version, bitbucketreponame, path, scanner):
        self.scanner=scanner
        self.domain=None
        self.broken = False
        self.qualitylevel=qualitylevel        
        self.description=""
        self.dependants=[]
        self.coderecipe=None
        self.blobs = {}
        self.releasenotes=""
        self.buildnr=0
        self.debug=False
        self.autobuild=False
        self.supportedplatforms=[]

        self.version=version
        self.versionint=self.version2int(version)

        self.name=name
        self.path=path
        
        domainnameList=[domain.domainname for domain in o.packages.domains if domain.bitbucketreponame==bitbucketreponame]
        if len(domainnameList)>0:
            self.domain=domainnameList[0]
        else:
            self.raiseError("Did not find domain")
            
                
        self.qualitylevel=qualitylevel

        cfgpath=o.system.fs.joinPaths(path,"owpackage.cfg")
        rnpath=o.system.fs.joinPaths(path,"releasenotes.wiki")
        descrpath=o.system.fs.joinPaths(path,"description.wiki")

        if not o.system.fs.exists(cfgpath):
            self.broken = True
            o.logger.log("Invalid Qpackage (%s). Cannot find configuration file: %s" % (name, cfgpath))
            return
        ini=o.tools.inifile.open(cfgpath)

        self.buildnr=ini.getValue("main","buildnr")
        if not ini.checkParam("main","debug"):            
            ini.setParam("main","debug",0)
        self.debug=ini.getValue("main","debug")==1
        if not ini.checkParam("main","autobuild"):
            ini.setParam("main","autobuild",0)
        self.autobuild=ini.getValue("main","autobuild")==1            
        self.supportedplatforms=ini.getValue("main","supportedplatforms")
        self.supportedplatforms=[item.lower() for item in self.supportedplatforms.split(",") if item.strip()<>""]

        tmp_restore = o.clients.bitbucket.getRepoConnection
        o.clients.bitbucket.getRepoConnection = monkey_getRepoConnection
        self._loadRecipe()  
        o.clients.bitbucket.getRepoConnection = tmp_restore        
        
        section="checksum"
        platforms2=ini.getParams(section)
        if platforms2==None:
            platforms2=[]
        for platform in platforms2:
            if platform not in self.supportedplatforms:
                self.raiseError("Found platform %s in bundle section of config file but platform does not exist." %platform )
                ini.removeParam(section,platform)
                
        for platform in self.supportedplatforms:
            if platform not in platforms2 and self.coderecipe<>False:
                self.raiseError("Found platform %s config but not in  bundle section and there is a recipe." %platform )
                #if self.qualitylevel=="unstable":
                    #if o.application.shellconfig.interactive:
                        #if o.console.askYesNo("Package %s_%s has a recipe but no bundle. Do you want to package and upload the bundle?" % (self.name, self.version)):
                            #result=o.packages.find(self.domain,self.name,self.version)
                            #if not result:
                                #raise RuntimeError("Found no Q-Package %s in %s with version %s" % (self.name, self.domain, self.version))
                            #elif len(result)==1:
                                #result[0].package()
                                #result[0].upload()        
                            #else:
                                #raise RuntimeError("Found more than one match for Q-Package %s in %s with version %s" % (self.name, self.domain, self.version)) 

        sections = ini.getSections()
        dependencies = [dep for dep in sections if dep.startswith("dep_")]
        for dep in dependencies:
            details = ini.getSectionAsDict(dep)
            details['name'] = dep[4:]
            self.dependants.append(details)
            
        ini=o.tools.inifile.open(cfgpath)

        if o.system.fs.exists(rnpath):
            self.releasenotes=o.system.fs.fileGetContents(rnpath)
        if o.system.fs.exists(descrpath):
            self.description=o.system.fs.fileGetContents(descrpath)                
        for platform in self.supportedplatforms:
            blobPath = o.system.fs.joinPaths(path, "blob_%s.info" % platform)
            if o.system.fs.exists(blobPath):
                self.blobs[platform] = o.system.fs.fileGetContents(blobPath)
            else:
                self.blobs[platform] = ""


    def raiseError(self,message):
        self.scanner.raiseError("%s %s %s %s: %s" % (self.domain,self.name,self.qualitylevel,self.version,message))

    def getQPobject(self):
        return o.packages.find(self.name,self.domain,self.version)

    def _loadModule(self,path):
        '''Load the Python module from disk using a random name'''
        #o.logger.log('Loading module %s' % path, 7)
        #Random name -> name in sys.modules
        def generate_module_name():
            '''Generate a random unused module name'''
            return '_tasklet_module_%d' % random.randint(0, sys.maxint)            
        modname = generate_module_name()
        while modname in sys.modules:
            modname = generate_module_name()
        
        #o.console.echo("Loading %s as %s" % (path, modname))
        module = imp.load_source(modname, path)
            
        return module        

    def _loadRecipe(self):

        recipepath=o.system.fs.joinPaths(self.path,"tasklets","codemanagement","1_defineCodeRecipe")
        if o.system.fs.exists(recipepath):
            paths=o.system.fs.listFilesInDir(recipepath,filter="*.py")
            if len(paths)==1:
                path=paths[0]
                #compile(o.system.fs.fileGetContents(path),path,'exec')                      
                try:
                    module=self._loadModule(path)
                except:
                    o.logger.exception("Failed to load recipe for %s" % self)
                    self.coderecipe=False
                    o.console.echo("Could not load recipe on %s (%s)" % (recipepath, path))
                                    
                if self.coderecipe != False:
                    params=o.core.params.get()
                    try:
                        params=module.main(q, i, params, service="", job="", tags="", tasklet="")
                        self.coderecipe=params.recipe
                        if self.coderecipe:
                            self.coderecipe.path=path
                        else:
                            self.coderecipe=False
                    except:
                        self.broken = True
                        self.coderecipe=False
                        o.console.echo("Broken QPackage. Could not execute recipe on %s (%s)" % (recipepath, path))

    def generateWikiPageGroupConfluence(self,wikigenerator=None):
        if self.broken:
            raise RuntimeError("Broken Qpackage")
            
        page=o.tools.wikigenerator.pageNewConfluence("")
        #page.addHeading(  ...
        page.addHeading(self.name)
        page.name = self.name
        
        #fill up the page (e.g. description, ...)
        page.addHeading("Qpackage Details", 3)
        page.addHeading("Description", 4)
        page.addMessage(self.description)
        page.addHeading("Quality Level", 4)
        page.addMessage(self.qualitylevel)
        page.addHeading("Version", 4)
        page.addMessage(self.version)
        page.addHeading("Build nr", 4)
        page.addMessage(self.buildnr)
        page.addHeading("Supported Platforms", 4)
        page.addMessage(self.supportedplatforms)


        #@todo P1 visualize dependancies
        page.addHeading("Dependencies", 3)
        for dep in self.dependants:
            page.addHeading(dep['name'],4)
            page.addDict(dep)
        
        #@todo P1 visualize code recipe and put link to coderecipe on trac see self.scanner.tracserver for addr
        page.addHeading("Code Recipe", 3)
        if self.coderecipe:
            page.addMessage(str(self.coderecipe))
        else:
            page.addMessage("Invalid Code Recipe!")
        
        #@todo P1 put link to each required part of repo (on default tip) on trac (so is easy for user to go and check out the code)
        
        #@todo P1 create a subpage with the  release notes
        pagern=o.tools.wikigenerator.pageNewConfluence("")
        pagern.name = self.name + " Release Notes"
        page.addHeading("Release Notes")
        page.addMessage(self.releasenotes)
        
        #@todo P1 create a subpage with the info from blobstor for the different platforms
        pagebl=o.tools.wikigenerator.pageNewConfluence("")
        pagern.name = self.name + " Blob Info"
        page.addHeading("Blob Info")
        page.addMessage(self.blobs)
        
        #add pages to pagegroup
        pages = {'p0' : page, 'p1' : pagern, 'p2' : pagebl}
        pagegroup=o.tools.wikigenerator.pageGroupNew(pages)
        
        
        return pagegroup

    def version2int(self,version):
        subversions=version.split(".")
        subversions.reverse()
        intversion=0
        for level in range(len(subversions)):
            intversion+=int(subversions[level])*(1000**(level))        
        return intversion

    def __str__(self):
        return "%s %s buildnr:%s %s %s" % (self.name,self.version,self.buildnr,self.qualitylevel,self.path)

    def __repr__(self):
        return self.__str__()


class QPackageMetadataScanner():

    def __init__(self):
        self.owpackages={} #dict with key the quality level
        self.tracserver="http://188.93.112.39:8080/"  #server which can be used to link to the code
        #o.system.fs.writeFile("ERRORS.TXT","\n########%s###########\n" % o.base.time.getLocalTimeHR(),append=True)
    
    def getAllQpackages(self,qualityLevels=None):
        qualityLevels = qualityLevels if qualityLevels is not None else []
        result=[]
        if qualityLevels==[]:
            qualityLevels.extend(self.owpackages.iterkeys())
        for key in qualityLevels:
            for item in self.owpackages[key]:
                result.append(item)
        return result    
    
    def copyBundlesToLocalBlobStor(self,remoteBlobStor=None,localBlobStor=None):
        """
        @param remoteBlobStor & localBlobStor, if none then "qplocal" & "qpremote" configured blobstores are used
        """
        if remoteBlobStor==None:
            remoteBlobStor=o.clients.blobstor.get("qpremote")
        if localBlobStor==None:
            localBlobStor=o.clients.blobstor.get("qpremote")
        qps=self.getAllQpackages()
        for qp in qps:
            from OpenWizzy.core.Shell import ipshell
            print "DEBUG NOW "
            ipshell()
                    
            remoteBlobStor.copyToOtherBlocStor(key,localBlobStor)
    
    def getRecipeItemsAsLists(self):
        qps=self.getAllQpackages()
        result=[]
        for qp in qps:
            if qp.coderecipe<>None and qp.coderecipe<>False:
                for item in qp.coderecipe.items:
                    bbaccount=item.coderepoConnection[0]
                    bbrepo=item.coderepoConnection[1]
                    branch=item.coderepoConnection[2]
                    basedir=o.system.fs.joinPaths(o.dirs.codeDir,bbaccount,bbrepo)
                    source = o.system.fs.joinPaths(basedir, item.source)
                    destination = o.system.fs.pathNormalize(item.destination, o.dirs.baseDir)                            
                    result.append([qp.qualitylevel,qp.name,qp.version,branch,source,destination])
        return result

    def _addQpackage(self,qualitylevel,qp):
        if not self.owpackages.has_key(qualitylevel):
            self.owpackages[qualitylevel]=[]
        self.owpackages[qualitylevel].append(qp)

    def raiseError(self,msg):
        o.console.echo("ERROR:: %s" % msg)
        #o.system.fs.writeFile("ERRORS.TXT", msg+"\n", append=True)

    def scan(self, allVersions=False, qualityLevels=None, packageNames=None):
        """
        Scan all packages

        @param allVersions:
        @type allVersions:
        @param qualityLevels: quality levels to scan
        @type qualityLevels: list(string)
        @param packageNames: names of the packages to scan
        @type packageNames: list(string)
        """
        codePath = o.system.fs.joinPaths(o.dirs.codeDir, 'incubaid')
        
        dirPaths = o.system.fs.listDirsInDir(codePath, )
        
        domainDirPaths = list()
        
        for dirPath in dirPaths:
            _, _, dirName = dirPath.rpartition('/')
            
            if dirName.startswith('qp5'):
                domainDirPaths.append(dirPath)
        
        #@todo P1 implement all versions behaviour
        for domainDirPath in domainDirPaths:
            if not qualityLevels:
                qualityLevels = o.system.fs.listDirsInDir(domainDirPath, dirNameOnly=True)            
                qualityLevels.remove('.hg')
            
            for qualityLevel in qualityLevels:        
                qualityLevelDirPath = o.system.fs.joinPaths(domainDirPath, qualityLevel)
                
                # if the quality level doesn't exists for this
                # domain continue to the next quality level
                if not o.system.fs.isDir(qualityLevelDirPath):
                    continue
                  
                qPackageDirs = o.system.fs.listDirsInDir(qualityLevelDirPath)
                
                for qPackageDir in qPackageDirs:
                    versionDirs = o.system.fs.listDirsInDir(qPackageDir, dirNameOnly=True)
                    versionMaxiInt = 0
                    
                    #look for highest version nr
                    for versionDir in versionDirs:
                        #try to sort them, calculate a nr
                        subVersions = versionDir.split('.')
                        subVersions.reverse()
                        
                        version=0
                        for level in range(len(subVersions)):
                            version += int(subVersions[level]) * (1000**(level))
                            
                            if version > versionMaxiInt:
                                versionMaxiInt = version
                                maxVersion = versionDir
                                
                    path = o.system.fs.joinPaths(qPackageDir, maxVersion)
                    pathPieces = path.strip('/').split('/')
                    pathPieces.reverse()
                    version = pathPieces[0]
                    name = pathPieces[1]
                    qualitylevel = pathPieces[2]
                    bitbucketreponame=pathPieces[3]
        
                    if not packageNames or name in packageNames:
                        qpModel = QPModel(qualitylevel, name, version,
                                bitbucketreponame, path, self)
                        self._addQpackage(qualityLevel, qpModel)
        
        #the scan is now completed we can now start doing our checks & manipulations
                                
    def detectDuplicateRecipeItemEntries(self,qualityLevels=None):
        qualityLevels = qualityLevels if qualityLevels is not None else []
        qps=self.getAllQpackages(qualityLevels)
        result= dict()
        duplicateResult = dict()
        destinations = []
        for qp in qps:
            if qp.coderecipe<>None and qp.coderecipe<>False:
                for item in qp.coderecipe.items:
                    bbaccount=item.coderepoConnection[0]
                    bbrepo=item.coderepoConnection[1]
                    branch=item.coderepoConnection[2]
                    basedir=o.system.fs.joinPaths(o.dirs.codeDir,bbaccount,bbrepo)
                    source = o.system.fs.joinPaths(basedir, item.source)
                    destination = o.system.fs.pathNormalize(item.destination, o.dirs.baseDir)
                    if not destination in result.keys():
                        result[destination] = [qp.qualitylevel,qp.name,qp.version, qp.coderecipe.path]
                        destinations.append(destination)
                    else:
                        duplicateResult[destination] = [qp.qualitylevel,qp.name,qp.version,qp.coderecipe.path,result[destination]]
                        o.console.echo("Duplicate entry found: ")
                        o.console.echo("%s -> %s" % (source,destination))
                        o.console.echo("Available in:")
                        o.console.echo("%s" % (qp.coderecipe.path))
                        o.console.echo("%s\n\n" % (result[destination][3]))
        for destination in destinations:
            for destination2 in destinations:
                checkdestination = destination
                if checkdestination[-1] != '/':
                    checkdestination += '/'
                if checkdestination in destination2 and destination != destination2:
                    o.console.echo("Parent directory issue: ")
                    o.console.echo("%s -> %s" % (destination,destination2))
                    o.console.echo("Available in:")
                    o.console.echo("%s" % (result[destination][3]))
                    o.console.echo("%s\n\n" % (result[destination2][3]))
        #return duplicateResult
    
    def detectDuplicateFiles(self, download=True, qualityLevels=None,
            output=True):
        """
        Detect duplicate files across all Q-Packages.

        WARNING: By default this method downloads all Q-Packages. Because this
        is quite slow, you can disable this with the `download` argument. You
        need to do the downloads if you want to work on the latest packages
        though!

        @param download: download all Q-Packages
        @type download: boolean
        @param qualityLevels: Quality levels to check
        @type qualityLevels: list(string)
        @param output: print the results to stdout
        @type output: boolean
        @return: An object containing all found file paths and their packages
        @rtype: DuplicateFilesResult
        """
        qualityLevels = qualityLevels if qualityLevels is not None else []
        qps=self.getAllQpackages(qualityLevels)
        result = dict()

        if download and o.application.shellconfig.interactive:
            download = o.console.askYesNo("Are you sure you want to download all packages?")

        if download:
            self.downloadAllQPackages(qualityLevels)

        qps = self.getAllQpackages(qualityLevels)
        for qp in qps:
            owpackage = qp.getQPobject()
            if owpackage:
                owpackage=owpackage[0]
                #info = [qp.qualitylevel, qp.name, qp.version, owpackage.getPathFiles()]
                info = qp
                files = o.system.fs.listFilesInDir(owpackage.getPathFiles(), recursive=True)
                for entry in files:
                    entry = entry.replace(owpackage.getPathFiles(),'')
                    for platform in qp.supportedplatforms:
                        entry = entry.replace('/' + platform,'')

                    entry = entry.strip()
                    if entry not in result:
                        result[entry] = [info]
                    else:
                        result[entry].append(info)


        result = DuplicateFilesResult(result)
        if output:
            result.echoDuplicatesByFile()
        return result

    def downloadAllQPackages(self, qualityLevels=None):
        qualityLevels = qualityLevels if qualityLevels is not None else []
        qps = self.getAllQpackages(qualityLevels)
        for qp in qps:
            owpackage = qp.getQPobject()
            if owpackage:
                owpackage=owpackage[0]
                owpackage.download()
                
                
    def _getPlatformChildrenRecursively(self, platformName):
        '''
        Gets the children of a platform in a recursive way
        
        @param platformName: name of the platform to get the children for
        @type platformName: String
        
        @return: a list with platform names
        @rtype: List
        '''
        
        platform = o.enumerators.PlatformType.getByName(platformName)
        
        children = platform.getChildren()
        childrenNames = list()
        
        for child in children:
            childName = str(child)
            childrenNames.append(childName)
        
            childChildrenNames = self._getPlatformChildrenRecursively(childName)
            childrenNames.extend(childChildrenNames)
            
        return childrenNames
    
    
    def _getPlatformParentRecursively(self, platformName):
        '''
        Gets the parents of a platform in a recursive way
        
        @param platformName: name of the platform to get the parents for
        @type platformName: String
        
        @return: a list with platform names
        @rtype: List
        '''
        
        platform = o.enumerators.PlatformType.getByName(platformName)
        
        parentNames = list()
        
        while platform.parent:
            parentName = str(platform.parent)
            parentNames.append(parentName)
            
            platform = platform.parent
            
        return parentNames
        

    def _getSupportedPlatformsFromConfig(self, config):
        '''
        Gets the supported platforms from a owpackage config
        
        @param config: owpackage config
        @type platformName: IniFile
        
        @return: a list with platform names
        @rtype: List
        '''
        
        platformCSV = config.getValue('main', 'supportedplatforms')
        platformCSV = platformCSV.strip(', ').replace(' ', '').lower()
        
        if platformCSV:
            return platformCSV.split(',')
        else:
            return list()
    
    
    def _getBundledPlatformsFromConfig(self, config):
        '''
        Gets the bundled platforms from a owpackage config
        
        @param config: owpackage config
        @type platformName: IniFile
        
        @return: a list with platform names
        @rtype: List
        '''
        
        if config.checkSection('checksum'):
            return config.getParams('checksum')
        else:
            return list()
        
    
    def detectPlatformConflicts(self, qualityLevels=None):
        '''
        Detects platform conflicts based on owpackages their config (owpackage.cfg)
        
        Possible conflicts:
        - no bundle available for a supported platform
        - bundle available for an unsupported platform
        
        @param qualityLevels: list of quality levels to detect conflicts for, defaults to list containing the default quality level
        @type qualityLevels: List
        '''
        
        if isinstance(qualityLevels, list) and not qualityLevels:
            raise RuntimeError('Invalid list of quality levels, should\'t be empty')
        
        qualityLevels = qualityLevels or ['default']
        qPackageModels = self.getAllQpackages(qualityLevels)
        
        for qPackageModel in qPackageModels:
            if qPackageModel.coderecipe != False:            
            
                qpName = qPackageModel.name
                qpPath = qPackageModel.path                            
                qpConfigPath = o.system.fs.joinPaths(qpPath, 'owpackage.cfg')
                    
                if not o.system.fs.exists(qpConfigPath):
                    raise RuntimeError('Could\'t find %(qPackageName)s owpackage config file at %(qpConfigPath)s' % {'qPackageName': qPackageModel.name,
                                                                                                                    'qpConfigPath': qpConfigPath})
                
                config = o.tools.inifile.open(qpConfigPath)
                            
                supportedPlatforms = self._getSupportedPlatformsFromConfig(config)
                supportedPlatform = list(set(supportedPlatforms))
                
                bundledPlatforms = self._getBundledPlatformsFromConfig(config)
                bundledPlatforms = list(set(bundledPlatforms))
                
                platformConflicts = dict()
                
                # Check supported platforms for conflicts
                #
                # Each supported platform should have a bundle for that supported
                # platform or a bundle for a parent of that supported platform            
                for supportedPlatform in supportedPlatforms:                
                    supportedPlatformParents = self._getPlatformParentRecursively(supportedPlatform)
                    
                    if set.intersection(set(supportedPlatformParents), set(bundledPlatforms)):
                        hasBundleForSupportedPlatformParent = True
                    else:
                        hasBundleForSupportedPlatformParent = False
                    
                    if supportedPlatform not in bundledPlatforms and not hasBundleForSupportedPlatformParent:
                        platformConflicts[supportedPlatform] = dict()
                        platformConflicts[supportedPlatform]['isSupported'] = 'yes'
                        platformConflicts[supportedPlatform]['isBundled'] = 'no'            
                
                # Check bundled platforms for conflicts
                #
                # Each bundled platform should be a supported platform
                # or a parent of one of the supported platforms
                supportedPlatformParents = list()
                
                for supportedPlatform in supportedPlatforms:                
                    parents = self._getPlatformParentRecursively(supportedPlatform)
                    supportedPlatformParents.extend(parents)
            
                supportedPlatformParents = list(set(supportedPlatformParents))
                
                for bundledPlatform in bundledPlatforms:                        
                    if bundledPlatform not in supportedPlatforms\
                       and bundledPlatform not in supportedPlatformParents:                    
                        platformConflicts[bundledPlatform] = dict()
                        platformConflicts[bundledPlatform]['isSupported'] = 'no'
                        platformConflicts[bundledPlatform]['isBundled'] = 'yes'
                        
                if platformConflicts:
                    qpInfo = {'name': qpName,
                              'configPath': qpConfigPath,
                              'hasRecipe': qPackageModel.coderecipe}
                    
                    self._printPlatformConflicts(qpInfo, platformConflicts)
            
            
    def _printPlatformConflicts(self, qpInfo, qpConflicts):
        '''
        Prints a owpackage its platform conflicts
        
        @param qpInfo: dict containing relevant owpackage info
        @type qpInfo: Dictionary
        
        @param qpConflicts: dict of platform conflicts
        @type qpConflicts: Dictionary
        '''
        
        o.console.echo('\n\n')
        o.console.echo('name:   %(name)s' % qpInfo)
        o.console.echo('config: %(configPath)s' % qpInfo)
        
        o.console.echo('recipe: yes')            
        o.console.echo('\n')
        o.console.echo('platform        supported    bundled')
        
        for platformName, conflictDetails in qpConflicts.iteritems():
            whiteSpaceA =  (16 - len(platformName)) * ' '
            whiteSpaceB =  (13 - len(conflictDetails['isSupported'])) * ' '
            
            line = platformName + whiteSpaceA + conflictDetails['isSupported'] + whiteSpaceB + conflictDetails['isBundled']
            
            o.console.echo(line)
            
            
    def detectConfigConflicts(self, qualityLevels=None):
        '''
        Detects owpackages config(owpackage.cfg) conflicts
        
        Possible conflicts:
        - no supported platforms found
        - obsolete supported platforms already supported by parents
        - duplicate supported platforms
        - duplicate bundled platforms
        
        @param qualityLevels: list of quality levels to detect conflicts for, defaults to list containing the default quality level
        @type qualityLevels: List
        '''
        qPackageModels = self.getAllQpackages(qualityLevels)
                
        for qPackageModel in qPackageModels:
            qpName = qPackageModel.name
            qpPath = qPackageModel.path                            
            qpConfigPath = o.system.fs.joinPaths(qpPath, 'owpackage.cfg')
                
            if not o.system.fs.exists(qpConfigPath):
                raise RuntimeError('Could\'t find %(qPackageName)s owpackage config file at %(qpConfigPath)s' % {
                    'qPackageName': qPackageModel.name, 'qpConfigPath': qpConfigPath})
            
            config = o.tools.inifile.open(qpConfigPath)
                        
            supportedPlatforms = self._getSupportedPlatformsFromConfig(config)
            
            conflicts = list()
            
            # check if there is at least one supported platform
            if not supportedPlatforms:
                conflicts.append('No supported platforms found')
                
            # check for obsolete supported platforms
            for supportedPlatform in supportedPlatforms:
                supportedPlatformParents = self._getPlatformParentRecursively(supportedPlatform)
                
                for supportedPlatformParent in supportedPlatformParents:
                    if supportedPlatformParent in supportedPlatforms:
                        conflicts.append('Supported platform %(platformName)s already covered by its parent platform %(parentPlatformName)s' % {
                            'platformName': supportedPlatform, 'parentPlatformName': supportedPlatformParent})
                                            
            # check for duplicate supported platforms
            duplicatePlatforms = set([platform for platform in supportedPlatforms if supportedPlatforms.count(platform) > 1])
            
            for duplicatePlatform in duplicatePlatforms:
                conflicts.append('Supported platform %(platformName)s duplicate found' % {
                    'platformName': duplicatePlatform})
                
            bundledPlatforms = self._getBundledPlatformsFromConfig(config)
            
            # check for duplicate bundled platforms
            duplicatePlatforms = set([platform for platform in bundledPlatforms if bundledPlatforms.count(platform) > 1])
            
            for duplicatePlatform in duplicatePlatforms:                
                conflicts.append('Bundled platform %(platformName)s duplicate found' % {
                    'platformName': duplicatePlatform})
                    
            if conflicts:
                qpInfo = {'name': qpName,
                          'configPath': qpConfigPath}
                
                self._printConfigConflicts(qpInfo, conflicts)
                
                        
    def _printConfigConflicts(self, qpInfo, qpConflicts):
        '''
        Prints a owpackage its config conflicts
        
        @param qpInfo: dict containing relevant owpackage info
        @type qpInfo: Dictionary
        
        @param qpConflicts: list of config conflicts
        @type qpConflicts: List
        '''
        
        o.console.echo('\n\n')
        o.console.echo('name:   %(name)s' % qpInfo)
        o.console.echo('config: %(configPath)s' % qpInfo)
        
        for qpConflict in qpConflicts:
            o.console.echo(qpConflict)
