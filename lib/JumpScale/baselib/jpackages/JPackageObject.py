try:
    import contextlib
except:
    pass
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import inspect
from JumpScale import j
from JumpScale.core.baseclasses import BaseType
from JumpScale.core.enumerators.PlatformType import PlatformType
from JumpScale.core.baseclasses.dirtyflaggingmixin import DirtyFlaggingMixin
from DependencyDef4 import DependencyDef4
from JPackageStateObject import JPackageStateObject
#from JumpScale.core.sync.Sync import SyncLocal
from JPackageIObject import JPackageIObject
from ActionManager import ActionManager

JPACKAGE_CFG = "jpackages.cfg"
BUILD_NR = "build_nr"
QUALITY_LEVEL = "quality_level"
IDENTITIES = "identities"

class JPackageObject(BaseType, DirtyFlaggingMixin):
    """
    Data representation of a JPackage, should contain all information contained in the jpackages.cfg
    """
    # All this information represents the package as in the repo..
    # the already install package may have different dependencies,
    # may have a higher build number
    domain  = j.basetype.string(doc='The domain this JPackage belongs to', allow_none=True, default=None)
    name    = j.basetype.string(doc='Name of the JPackage should be lowercase', allow_none=False)
    version = j.basetype.string(doc='Version of a string', allow_none=False)


    buildNr  = j.basetype.integer(doc='Build number of the JPackage', allow_none=False, default=0)
    #bundleNr = j.basetype.integer(doc='Build number of the Bundle', allow_none=False, default=0)
    #metaNr   = j.basetype.integer(doc='Build number of the MetaData', allow_none=False, default=0)

    #should be readonly
    # @todo check why this should be read only because this class provides public methods that alter these lists which doesn't make sense
    supportedPlatforms = j.basetype.list(doc='List of PlatformTypes', allow_none=False, default=list())
    tags               = j.basetype.list(doc='list of tags describing the JPackage', allow_none=True, default=list())
    description        = j.basetype.string(doc='Description of the JPackage, can be larger than the description in the VList4', allow_none=True, flag_dirty=True, default='')
    dependencies       = j.basetype.list(doc='List of DependencyDefinitions for this JPackage', allow_none=True, default=list())
    #guid               = j.basetype.string(doc='Unique global id', allow_none=False, flag_dirty=True, default='')
    #lastModified       = j.basetype.float(doc='When was this package last modified (time.time)', allow_none=False, flag_dirty=True, default='')

    def __init__(self, domain, name, version):
        """
        Initialization of the JPackage

        @param domain:  The domain that the JPackage belongs to, can be a string or the DomainObject4
        @param name:    The name of the JPackage
        @param version: The version of the JPackage
        """

        ##j.logger.log('Initializing the JPackage Object %s - %s - %s'%(domain, name, version), 6)
        #checks on correctness of the parameters
        if not domain:
            raise ValueError('The domain parameter cannot be empty or None')
        if not name:
            raise ValueError('The name parameter cannot be empty or None')
        if not version:
            raise ValueError('The version parameter cannot be empty or None')
        self.domain = domain
        self.name = name
        self.version = version
        self.buildNr=-1
        self.taskletsChecksum=""    
        self.bundles={}
        
        self.metadataPath=self.getPathMetadata()
        
        self.description=""
        
        self.metadata=None
                
        self.__init=False

        self._init()


    def _init(self):
        if self.__init==False:
            self.load()
        self.__init=True

    def init(self):

        #create defaults for new jpackages
        hrddir=j.system.fs.joinPaths(self.metadataPath,"hrd")
        if not j.system.fs.exists(hrddir):  
            new=True
            extpath=inspect.getfile(self.__init__)
            extpath=j.system.fs.getDirName(extpath)
            src=j.system.fs.joinPaths(extpath,"templates")
            j.system.fs.copyDirTree(src,self.metadataPath)                                                  
        
        self.hrd=j.core.hrd.getHRDTree(hrddir)

        if self.hrd.get("qp.name",checkExists=True)<>self.name:
            self.hrd.set("qp.name",self.name)
        if self.hrd.get("qp.version",checkExists=True)<>self.version:                
            self.hrd.set("qp.version",self.version)    
        descr=self.hrd.get("qp.description",checkExists=True)
        if descr<>False and descr<>"":
            self.description=descr
        if descr<>self.description:                
            self.hrd.set("qp.description",self.description)                      

        

        supportedPlatforms=self.hrd.getList("qp.supportedplatforms")

        for platform in self.supportedPlatforms:
            j.system.fs.createDir(self.getPathFilesPlatform(platform))        

        self.hrd.applyOnDir(self.metadataPath,changeContent=False)


    def load(self,hrdDir=None,position=""):                

        #create defaults for new jpackages
        hrddir=j.system.fs.joinPaths(self.metadataPath,"hrd")
        if not j.system.fs.exists(hrddir):  
            self.init()
        self.hrd=j.core.hrd.getHRDTree(hrddir)
        self._clear()
        self.buildNr = self.hrd.getInt("qp.buildnr")
        self.debug = self.hrd.getBool("qp.debug")
        self.export = self.hrd.getBool("qp.export")
        self.autobuild = self.hrd.getBool("qp.autobuild")
        self.taskletsChecksum = self.hrd.get("qp.taskletschecksum")
        self.supportedPlatforms = [j.enumerators.PlatformType.getByName(p) for p in self.hrd.getList("qp.supportedplatforms")]
        self.bundles = self.hrd.getDict("qp.bundles") #dict with key platformkey and val the hash of bundle
        
        self.processDependencies()

        j.packages.jumpscale.getDomainObject(self.domain)

        self.blobstorRemote = None
        self.blobstorLocal = None

        self.actions = None

    def loadActions(self):
        if self.actions <> None:
            return

        self.hrd.add2tree(j.system.fs.joinPaths(j.dirs.cfgDir,"hrd"))        

        j.system.fs.createDir(self.getPathActiveHRD())
        self.hrd.add2tree(self.getPathActiveHRD(),position="active") 
        
        j.system.fs.copyDirTree(j.system.fs.joinPaths(self.metadataPath,"actions"),self.getPathActions())        
        
        self.hrd.applyOnDir(self.getPathActions(),"") #make sure params are filled in in actions dir

        self.actions = ActionManager(self)
        
        do = j.packages.jumpscale.getDomainObject(self.domain)
        if do.blobstorremote.strip() <> "":
            self.blobstorRemote = j.clients.blobstor.get(do.blobstorremote)

        if do.blobstorlocal.strip() <> "":
            self.blobstorLocal = j.clients.blobstor.get(do.blobstorlocal)

    def getDebugMode(self):
        return self.getState().debugMode

    def setDebugMode(self):
        self.getState().setDebugMode()
        print self.getDebugMode()

    def removeDebugMode(self):
        self.getState().setDebugMode(mode=0)
        print self.getDebugMode()

###############################################################
############  MAIN OBJECT METHODS (DELETE, ...)  ##############
###############################################################

    def delete(self):
        """
        Delete all bundles, metadata, files of the jpackages
        """
        self._init()
        if j.application.shellconfig.interactive:
            do = j.gui.dialog.askYesNo("Are you sure you want to remove %s_%s_%s, all bundles, metadata & files will be removed" % (self.domain, self.name, self.version))
        else:
            do = True
        if do:
            path = j.packages.jumpscale.getDataPath(self.domain, self.name, self.version)
            j.system.fs.removeDirTree(path)
            path = j.packages.jumpscale.getMetadataPath(self.domain, self.name,self.version)
            j.system.fs.removeDirTree(path)
            path = j.packages.jumpscale.getQPActionsPath(self.domain, self.name,self.version)
            j.system.fs.removeDirTree(path)
            for f in j.system.fs.listFilesInDir(j.packages.jumpscale.getBundlesPath()):
                baseName = j.system.fs.getBaseName(f)
                if baseName.split('__')[0] == self.name and baseName.split('__')[1] == self.version:
                    j.system.fs.deleteFile(f)
            #@todo over ftp try to delete the targz file (less urgent), check with other quality levels to make sure we don't delete files we should not delete

    def save(self, new=False):
        """
        Creates a new config file and saves the most important jpackages params in it

        @param new: True if we are saving a new Q-Package, used to ensure backwards compatibility
        @type new: boolean
        """      
        self._log('saving jpackages data to ' + self.metadataPath)

        if self.buildNr == "":
            self._raiseError("buildNr cannot be empty")
        
        #cfg.setChecksums(self.bundles, write=False)  #@todo !!!!!!!!!!!

        self.hrd.set("qp.debug",self.debug)
        self.hrd.set("qp.buildnr",self.buildNr)        
        self.hrd.set("qp.export",self.export)
        self.hrd.set("qp.autobuild",self.autobuild)
        self.hrd.set("qp.taskletschecksum",self.taskletsChecksum)
        self.hrd.set("qp.supportedplatforms",self.supportedPlatforms)
        self.hrd.set("qp.bundles",self.bundles)

        for idx, dependency in enumerate(self.dependencies):
            self._addDependencyToHRD(idx, dependency.domain, dependency.name, dependency.supportedPlatforms,
                                         minversion=dependency.minversion,
                                         maxversion=dependency.maxversion,
                                         dependencytype=dependency.dependencytype)

    def _addDependencyToHRD(self, idx, domain, name, supportedplatforms, minversion, maxversion, dependencytype):
        hrd = self.hrd.getHrd().getHRD('qp.name')
        basekey = 'qp.dependency.%s.%%s' % idx
        def setValue(name, value):
            hrd.set(basekey % name, value)

        setValue('domain', domain)
        setValue('name', name)
        setValue('supportedplatforms', supportedplatforms)
        setValue('minversion', minversion)
        setValue('maxversion', maxversion)
        setValue('dependencytype', dependencytype)

    def addActiveHrdFile(self,name,content):
        activehrd=self.getPathActiveHRD()
        j.system.fs.createDir(activehrd)
        j.system.fs.writeFile(filename=j.system.fs.joinPaths(activehrd,"%s.hrd"%name),contents=content)
        self.hrd.add2tree(activehrd,position="active")         

##################################################################################################
###################################  CONFIG FILE HANDLING  #######################################
##################################################################################################


    def processDependencies(self):
        self.dependencies = []

        def depFromInfo(dependencyInfo):
            dep = DependencyDef4()
            dep.name = dependencyInfo["name"]
            dep.domain = dependencyInfo["domain"]
            dep.minversion = dependencyInfo["minversion"]
            dep.maxversion = dependencyInfo["maxversion"]
            dep.supportedPlatforms = dependencyInfo["supportedplatforms"]
            dep.dependencytype = j.enumerators.DependencyType4.getByName(dependencyInfo['dependencytype'])
            return dep

        addedstuff = set()
        for key in self.hrd.prefix('qp.dependency'):
            parts = key.split('.')
            if parts[2] in addedstuff:
                continue
            key = "%s.%%s" % (".".join(parts[:3]))
            dependencyInfo = dict()
            for depkey in ('name', 'domain', 'minversion', 'maxversion', 'dependencytype'):
                dependencyInfo[depkey] = self.hrd.get(key % depkey)
                
            dependencyInfo['supportedplatforms'] = [ j.enumerators.PlatformType.getByName(x) for x in  self.hrd.getList(key % 'supportedplatforms') ]
            dep = depFromInfo(dependencyInfo)
            addedstuff.add(parts[2])
            self.dependencies.append(dep)


        #self.requiredblobs = cfg.getRequiredBlobs() #TODO P1

    def addDependency(self, domain, name, supportedplatforms, minversion, maxversion, dependencytype):
        dep = DependencyDef4()
        dep.name = name
        dep.domain = domain
        dep.minversion = minversion
        dep.maxversion = maxversion
        dep.supportedPlatforms = supportedplatforms
        dep.dependencytype = j.enumerators.DependencyType4.getByName(dependencytype)
        self.dependencies.append(dep)

#############################################################################
####################################  GETS  #################################
#############################################################################

    def getIsPreparedForUpdatingFiles(self):
        """
        Return true if package has been prepared
        """
        prepared = self.getState().prepared
        if prepared == 1:
            return True
        return False

    def getDependingInstalledPackages(self, recursive=False):
        """
        Return the packages that are dependent on this packages and installed on this machine
        This is a heavy operation and might take some time
        """
        ##self.assertAccessable()
        if self.getDependingPackages(recursive=recursive) == None:
            raise RuntimeError("No depending packages present")
        [p for p in self.getDependingPackages(recursive=recursive) if p.isInstalled()]

    def getDependingPackages(self, recursive=False, platform=j.enumerators.PlatformType.GENERIC):
        """
        Return the packages that are dependent on this package
        This is a heavy operation and might take some time
        """
        ##self.assertAccessable()
        return [p for p in j.packages.jumpscale.getJPackageObjects() if self in p.getDependencies(recursive=recursive, platform=platform)]


    def getState(self):
        ##self.assertAccessable()
        """
        from dir get [qbase]/cfg/jpackages/state/$jpackagesdomain_$jpackagesname_$jpackagesversion.state
        is a inifile with following variables
        * lastinstalledbuildNr
        * lastaction
        * lasttag
        * lastactiontime  epoch of last time an action was done
        * currentaction  ("" if no action current)
        * currenttag ("" if no action current)
        * lastexpandedbuildNr  (means expanded from tgz into jpackages dir)
        @return a JpackageStateObject
        """
        return JPackageStateObject(self)

    def getVersionAsInt(self):
        """
        Translate string version representation to a number
        """
        ##self.assertAccessable()
        #@todo
        version = self.version
        return float(version)

    def getPathActions(self):
        """
        Return absolute pathname of the package's metadatapath
        """
        return j.packages.jumpscale.getQPActionsPath(self.domain, self.name, self.version)

    def getPathActiveHRD(self):
        """
        Return absolute path to active hrd of package
        """
        return j.packages.jumpscale.getQPActiveHRDPath(self.domain, self.name, self.version)

    def getPathMetadata(self):
        """
        Return absolute pathname of the package's metadatapath active
        """
        return j.packages.jumpscale.getMetadataPath(self.domain, self.name, self.version)


    def getPathFiles(self):
        """
        Return absolute pathname of the jpackages's filespath
        """
        ##self.assertAccessable()
        return j.packages.jumpscale.getDataPath(self.domain, self.name, self.version)


    def getPathFilesPlatform(self, platform):
        """
        Return absolute pathname of the jpackages's filespath
        """
        ##self.assertAccessable()
        path =  j.system.fs.joinPaths(self.getPathFiles(), str(platform))
        return path


    def getPathSourceCode(self):
        """
        Return absolute path to where this package's source can be extracted to
        """
        raise NotImplementedError()
        #return j.system.fs.joinPaths(j.dirs.varDir, 'src', self.name, self.version)


    def getBundlePlatforms(self):
        """
        Return the list of platforms on which the bundle can be installed.
        """

        platforms = list()

        for supportedPlatform in self.supportedPlatforms:
            platform = supportedPlatform
            platform = j.enumerators.PlatformType.__dict__[(str(platform).upper())]
            
            while platform != None:
                platforms.append(platform)
                platform = platform.parent

        return list(set(platforms))

    def getHighestInstalledBuildNr(self):
        """
        Return the latetst installed buildnumber
        """
        ##self.assertAccessable()
        return self.getState().lastinstalledbuildnr

    def getBrokenDependencies(self, platform=None):
        """
        Return a list of dependencies that cannot be resolved
        """
        if platform==None:
            platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")
        broken = []
        for dep in self.dependencies:   # go over my dependencies
                                        # Do this without try catch
                                        # pass boolean to findnewest that it should return None instead of fail
            try:
                j.packages.jumpscale.findNewest(domain=dep.domain, name=dep.name, minversion=dep.minversion, maxversion=dep.maxversion, platform=platform)
            except Exception, e:
                print str(e)
                broken.append(dep)
        return broken


    def pm_getDependencies(self, dependencytype=None, platform=j.enumerators.PlatformType.GENERIC, recursive=False, depsfound=None, parent=None, depth=0, printTree=False, padding='', isLast=False, encountered=False):
        """
        Return the dependencies for the JPackage

        @param depsfound [[$domain,$name,$version]]
        @return [[parent,jpackagesObject]]
        """
        if j.enumerators.DependencyType4.check(dependencytype) == False and dependencytype <> None:
            raise RuntimeError("parameter dependencytype in get dependencies needs to be of type: j.enumerators.DependencyType4, now %s" % dependencytype)
        if j.enumerators.PlatformType.check(platform) == False and platform <> None:
            raise RuntimeError("parameter platform in get dependencies needs to be of type: j.enumerators.PlatformType, now %s" % platform)
        depsfoundToReturn = []

        if depsfound == None:
            depsfound = set()

        childPadding = ''
        if printTree: # print myself
            end = ''
            # The dependencies my children visit do not affect the dependency i visit
            # but my children cannot decent into dependency I already decented into
            end = '*'      if encountered            else ''
            prefix = '\''  if isLast else '|'
            childPadding = padding + (' ' if isLast else '|') + '   '
            j.console.echo(padding + prefix + '--' + str(self) + end)

        if not encountered:
            for idx, dep in enumerate(self.dependencies): # go over my dependencies
                found = False
                if dep.dependencytype == dependencytype or dependencytype == None:
                    for plat in dep.supportedPlatforms:
                        #print str(plat) + '.hasParent(' + str(platform) + ')'
                        if plat.has_parent(platform):
                            found = True
                        #@DEBUG please review this change
                        if platform.has_parent(plat):
                            found = True

                if found:
                    #dependenciesAlreadyFound=[d for parent,d in depsfound]
                    # If We encounter an exception keep printing the tree
                    # so we can see all missing packages in one go

                    # If platform is generic, than we look for a package supporting generic?
                    # Thus we look for a package supporting all platforms? Or do we look for packages supporting any of the enumerated platforms?
                    # We need the do the latter, so the definition of findNewest should reflect this!
                    depjpackage = dep.getPackage(platform=platform, returnNoneIfNotFound=True)
                    if not depjpackage:
                        self._log('dependency ' + str(dep) + ' could not be resolved for package ' + str(self))

                        raise RuntimeError('\
Could not find the %(qpDepName)s jpackages which is a dependency of the %(qpName)s jpackages, \
updating the metadata for the %(qpDepDomain)s jpackages domain might resolve this issue' % {'qpName': self.name,
                                                                                           'qpDepName': dep.name,
                                                                                           'qpDepDomain': dep.domain})


                    childEncountered = str(depjpackage) in depsfound
                    childDeptsFound  = depsfound
                    if not childEncountered:
                        depsfound.add(str(depjpackage))
                        depsfoundToReturn.append(depjpackage)
                    if printTree:
                        #childDeptsFound = set(depsfound)
                        pass
                    if recursive:
                        depsfoundToReturn.extend(depjpackage.pm_getDependencies(dependencytype, platform,recursive, childDeptsFound,depjpackage, depth + 1, printTree, childPadding, idx == len(self.dependencies) - 1, childEncountered))
        return depsfoundToReturn #only returns the new ones



    def getDependencyTree(self, platform=None):
        """
        Return the Build dependencies for the JPackage

        @param platform see j.enumerators.PlatformType....
        """
        if platform == None:
            platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")

        self.pm_getDependencies(None, platform, recursive=True, printTree=True)

    def getBuildDependencyTree(self, platform=None):
        """
        Return the Build dependencies for the JPackage
        """
        if platform == None:
            platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")
        self.pm_getDependencies(j.enumerators.DependencyType4.BUILD, platform, recursive=True, printTree=True)

    def getRuntimeDependencyTree(self, platform=None):
        """
        Return the runtime dependencies for the JPackage, will not recurse into the dependencies
        """
        if platform == None:
            platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")

        self.pm_getDependencies(j.enumerators.DependencyType4.RUNTIME, platform, recursive=True, printTree=True)

    def getDependencies(self, platform=None, recursive=True):
        """
        Return the Build dependencies for the JPackage
        """
        if platform == None:
            platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")
        res = self.pm_getDependencies(None, platform,recursive)
        res.sort()
        return res

    def getBuildDependencies(self, platform=None, recursive=False):
        """
        Return the Build dependencies for the JPackage
        """
        if platform == None:
            platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")
        if recursive == None:
            recursive = j.console.askYesNo( "Recursive?")
        res = self.pm_getDependencies(j.enumerators.DependencyType4.BUILD, platform, recursive)
        res.sort()
        return res

    def getRuntimeDependencies(self, platform=None, recursive=False):
        """
        Return the runtime dependencies for the JPackage, will not recurse into the dependencies
        """
        if platform == None:
            platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")
        if recursive == None:
            recursive = j.console.askYesNo( "Recursive?")
        res = self.pm_getDependencies(j.enumerators.DependencyType4.RUNTIME, platform, recursive)
        res.sort()
        return res

    def getQualityLevels(self, force=False):
        """
        Get a dict with quality levels as keys and the build numbers on those
        levels as values.

        @return: a dict with quality levels as keys and build numbers as values
        @rtype: dict(str, int)
        """
        domain = self._getDomainObject()

        def getQualityLevelInfo(cfg):
            buildNr = cfg.getBuildNumber()
            identities = cfg.getIdentities()
            return {
                    BUILD_NR: buildNr,
                    IDENTITIES: identities
                    }

        qualitylevels = {}
        for qualitylevel in domain.getQualityLevels():
            cfgPath = self._getConfigPath(qualitylevel)
            if j.system.fs.exists(cfgPath):
                cfg = self._getConfig(qualitylevel)
                info = getQualityLevelInfo(cfg)
                qualitylevels[qualitylevel] = info
        return qualitylevels

    def promote(self, buildNr, fromQl, toQl, force=False):
        """
        Promote the build with number `buildNr` from quality level `fromQl` to
        quality level `toQl`. If the build number on `toQl` is higher than the
        build number on `fromQl`, a ValueError will be raised, unless `force` is
        passed as True. If there is no build with number `buildNr` on `fromQl`,
        a ValueError will be raised.

        @param buildNr: build number to promote
        @type buildNr: int
        @param fromQl: quality level the files should be taken from
        @type fromQl: string
        @param toQl: quality level the files should be copied to
        @type toQl: string
        @param force: promote even of toQl is on a higher quality level
        @type force: boolean
        """
        domain = self._getDomainObject()
        hgc = domain.mercurialclient

        def getDestPath(p):
            parts = p.split(os.path.sep)
            parts[0] = toQl
            return os.path.sep.join(parts)

        def copy(repo, filectx):
            subPath = filectx.path()
            destSubPath = getDestPath(subPath)
            destPath = j.system.fs.joinPaths(repo.root, destSubPath)
            destDir = j.system.fs.getDirName(destPath)
            if not j.system.fs.isDir(destDir):
                j.system.fs.createDir(destDir)
            data = filectx.data()
            with open(destPath, 'w') as f:
                f.write(data)

        nodeId = None
        for candidateNodeId, cfg in self._iterCfgHistory(fromQl):
            n = cfg.getBuildNumber()
            if n == buildNr:
                nodeId = candidateNodeId
            # We want the *first* metadata commit with a certain build number.
            # So we break only when the buildnumber becomes smaller thant the
            # build number that we we want to promote.
            if n < buildNr:
                break

        if not nodeId:
            raise ValueError("No build with number %s was found on quality "
                "level %s" % (buildNr, fromQl))

        try:
            toCfg = self._getConfig(toQl)
            toBuildNr = toCfg.getBuildNumber()
            if toBuildNr >= buildNr and not force:
                raise ValueError("Build number on the target quality level is "
                    "%s, which is greater than or equal to the argument build "
                    "number %s; if you are sure you want to promote down, "
                    "pass the force argument as True" % (toBuildNr, buildNr))
        except LookupError:
            j.logger.exception("There is no Q-Package config file on quality "
                    "level %s yet" % toQl, 5)

        toPath = domain.getJPackageMetadataDir(toQl, self.name, self.version)
        j.system.fs.removeDirTree(toPath)
        j.system.fs.createDir(toPath)
        subPath1 = os.path.sep.join([fromQl, self.name, self.version, "**", "*"])
        subPath2 = os.path.sep.join([fromQl, self.name, self.version, "*"])
        subPaths = [subPath1, subPath2]
        hgc.walk(nodeId, subPaths, copy)

#############################################################################
################################  CHECKS  ###################################
#############################################################################

    def hasModifiedFiles(self):
        """
        Check if files are modified in the JPackage files
        """
        ##self.assertAccessable()
        if self.getState().prepared == 1:
            return True
        return False

    def hasModifiedMetaData(self):
        """
        Check if files are modified in the JPackage metadata
        """
        ##self.assertAccessable()
        return self in j.packages.jumpscale.getDomainObject(self.domain).getJPackageTuplesWithModifiedMetadata()

    def isInstalled(self):
        """
        Check if the JPackage is installed
        """
        ##self.assertAccessable()
        return self.getState().lastinstalledbuildnr != -1

    def supportsPlatform(self, platform):
        """
        Check if a JPackage can be installed on a platform
        """
        if not platform:
            return True
        for supportedPlatform in self.supportedPlatforms:
            if platform.has_parent(supportedPlatform):
                return True
        # To be complete we should check if we support all children of the platform
        # Then to we support the platform.. these situation may occur in the packages


#############################################################################
#################################  ACTIONS  ################################
#############################################################################

    def update(self):
        """
        Reinstall the package
        """
        self.actions.install()

    def export(self, url):
        """
        Create export, run the export tasklet(s)

        @param url: where to back up to, e.g. : ftp://login:passwd@10.10.1.1/myroot/
        """
        self.actions.export(url=url)
        self._log('export to %s '%(url))


    def importt(self, url):
        """
        Restore a backup, run, the restore tasklet(s)

        @param url: location of the backup, e.g. : ftp://login:passwd@10.10.1.1/myroot/
        """
        self.actions.importt(url=url)
        self._log('import from %s '%(url))

    def start(self):
        """
        Start the JPackage, run the start tasklet(s)
        """
        self.actions.start()
        self._log('start')

    def stop(self):
        """
        Stop the JPackage, run the stop tasklet(s)
        """
        self.actions.stop()
        self._log('stop')


    def restart(self):
        """
        Restart the JPackage
        """
        self.stop()
        self.start()

    def isrunning(self):
        """
        Check if application installed is running for jpackages
        """
        self.loadActions()
        self.actions.isrunning()
        self._log('isrunning')


    def _isHostPlatformSupported(self, platform):
        '''
        Checks if a given platform is supported, the checks takes the
        supported platform their parents in account.

        @param platform: platform to check
        @type platform: j.enumerators.PlatformType

        @return: flag that indicates if the given platform is supported
        @rtype: Boolean
        '''

        supportedPlatformPool = list()

        for platform in self.supportedPlatforms:
            while platform != None:
                supportedPlatformPool.append(platform)
                platform = platform.parent

        if platform in supportedPlatformPool:
            return True
        else:
            return False


    def install(self, dependencies=True, download=True, reinstall=False):
        """
        Install the JPackage

        @param dependencies: if True, all dependencies will be installed too
        @param download:     if True, bundles of package will be downloaded too
        @param reinstall:    if True, package will be reinstalled
        """
        self.loadActions()
        #hostPlatformSupported = self._isPlatformSupported(hostPlatform)

        #if not hostPlatformSupported:
        #   raise RuntimeError('JPackage %(jPackageName)s doesn\'t support the host platform %(platformName)s'
        #                       % {'jPackageName': str(self), 'platformName': hostPlatform})

        #self.checkProtectedDirs(redo=True,checkInteractive=True)
        action="install"

        if j.packages.jumpscale._actionCheck(self,action):
            return True


        # If I am already installed assume my dependencies are also installed
        if self.buildNr <> -1 and self.buildNr <= self.getState().lastinstalledbuildnr and not reinstall:
            self._log('already installed')
            return # Nothing to do

        j.action.start('Installing %s' % str(self), 'Failed to install %s' % str(self))

        if dependencies:            
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.install(dependencies, download, reinstall)

        tag = "install"
        action = "install"
        if download and self.debug <> True:
            self.download(dependencies=False)

        if self.debug or reinstall or self.buildNr > self.getState().lastinstalledbuildnr:

            src=j.system.fs.joinPaths(self.getPathMetadata(),"hrdactive")
            dest=j.system.fs.joinPaths(self.getPathActiveHRD())
            j.system.fs.createDir(dest)
            j.system.fs.copyDirTree(src,dest) 

            self.hrd.applyOnDir(self.metadataPath,changeContent=False)
            
            self.hrd.add2tree(src,position="active") 


        if self.debug <> True and reinstall or self.buildNr > self.getState().lastinstalledbuildnr:
            #print 'really installing ' + str(self)
            self._log('installing')
            if self.getState().checkNoCurrentAction == False:
                raise RuntimeError ("jpackages is in inconsistent state, ...")                

            self.actions.install()
            self.getState().setLastInstalledBuildNr(self.buildNr)
        elif self.debug:
            #only the link functionality for now
            self.codeLink(dependencies=False, update=True, force=True)


        # q.extensions.pm_sync()

        j.action.stop(False)


    def uninstall(self, unInstallDependingFirst=False):
        """
        Remove the JPackage from the sandbox. In case dependent JPackages are installed, the JPackage is not removed.

        @param unInstallDependingFirst: remove first dependent JPackages
        """
        # Make sure there are no longer installed packages that depend on me
        ##self.assertAccessable()
        self.loadActions()
        if unInstallDependingFirst:
            for p in self.getDependingInstalledPackages():
                p.uninstall(True)
        if self.getDependingInstalledPackages(True):
            raise RuntimeError('Other package on the system dependend on this one, uninstall them first!')

        tag = "install"
        action = "uninstall"
        state = self.getState()
        if state.checkNoCurrentAction == False:
            raise RuntimeError ("jpackages is in inconsistent state, ...")
        self._log('uninstalling' + str(self))
        self.actions.uninstall()
        state.setLastInstalledBuildNr(-1)

    def isUninstallable(self):
        # Does no work since we cannot look inside a package..
        return True
        #return self._hasTasklet('uninstall')

    def prepareForUpdatingFiles(self, suppressErrors=False):
        """
        After this command the operator can change the files of the jpackages.
        Files do not aways come from code repo, they can also come from jpackages repo only
        """
        j.system.fs.createDir(self.getPathFiles())
        if  self.getState().prepared <> 1:
            if not self.isNew():
                self.download(suppressErrors=suppressErrors)
                self._expand(suppressErrors=suppressErrors)
            self.getState().setPrepared(1)

    def isNew(self):
        # We are new when our files have not yet been committed
        # check if our jpackages.cfg file in the repo is in the ignored or added categories
        domainObject = self._getDomainObject()
        cfgPath = j.system.fs.joinPaths(self.metadataPath, JPACKAGE_CFG)
        return not domainObject._isTrackingFile(cfgPath)

    def copyFiles(self, destination=""):
        """
        Copy the files from package dirs (/opt/qbase5/var/jpackages/...) to their proper location in the sandbox.

        @param destination: destination of the files, default is the sandbox
        """
        return self.copyFileParts("", destination)

    def copyFileParts(self, subdir, destination=""):
        _jpackagesDir = self.getPathFiles()

        self._log('Syncing %s to sandbox' % _jpackagesDir)
        platformDirsToCopy = self._getPlatformDirsToCopy()
        if destination == "":
            destination = j.dirs.baseDir
        for platformDir in platformDirsToCopy:
            self._log('Syncing files in <%s>' % platformDir)
            platformDir = j.system.fs.joinPaths(platformDir, subdir)
            self._copyFilesTo(platformDir, destination)

    def _copyFilesTo(self, sourceDir, destination):
        """
        Copy Files

        @param sourceDir: directory to copy files from
        @param destination: directory to copy files to
        """
        def createAncestors(file):
            # Create the ancestors
            j.system.fs.createDir(j.system.fs.getDirName(file))

        if sourceDir [-1] != '/':
            sourceDir = sourceDir + '/'
        prefixHiddenFile = sourceDir + '.'

        if j.system.fs.isDir(sourceDir):
            files = j.system.fs.walk(sourceDir, recurse=True, return_folders=True, followSoftlinks=False)
            for file in files:
                # Remove hidden files and directories:
                if file.find(prefixHiddenFile) == 0 :
                    continue
                destinationFile = j.system.fs.joinPaths(destination, file[len(sourceDir):])
                _copy = True

                if destinationFile in j.dirs.protectedDirs:
                    j.console.echo( "Skipping %s because it's protected" % destinationFile)
                    _copy = False

                if _copy:
                    for protectedDir in j.dirs.protectedDirs:
                        # Add a '/' if needed, so we don't accidentally filter
                        # out /home/jumpscale if /home/p is protected
                        if protectedDir and protectedDir[-1] != os.path.sep:
                            protectedDir = protectedDir + os.path.sep

                        if destinationFile.startswith(protectedDir):
                            j.console.echo( "Skipping %s because %s is protected" % (
                                        destinationFile, protectedDir))
                            _copy = False
                            break

                if _copy:
                    self._log("Copying <%s>" % destinationFile)

                    createAncestors(destinationFile)
                    if j.system.fs.isLink( file ) :
                        j.system.fs.symlink(os.readlink( file ), destinationFile, overwriteTarget=True )
                    elif j.system.fs.isDir (file) :
                        j.system.fs.createDir(destinationFile )
                    else:
                        j.system.fs.copyFile(file, destinationFile)

            self._log('Syncing done')
        else:
            self._log('Directory <%s> does not exist' % sourceDir)


    def configure(self, dependencies=False):
        """
        Configure the JPackage after installation, via the configure tasklet(s)
        """
        self._log('configure')
        self.loadActions()
        j.action.start('Configuring %s' % str(self), 'Failed to configure %s' % str(self))
        if dependencies:
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.configure()
        self.actions.configure()
        self.getState().setIsPendingReconfiguration(False)
        j.action.stop(False)

    def codeExport(self, dependencies=False, update=None):
        """
        Export code to right locations in sandbox or on system
        code recipe is being used
        only the sections in the recipe which are relevant to you will be used
        """
        self.loadActions()
        j.action.start('Export %s\n' % str(self), 'Failed to export code for %s' % str(self))
        if dependencies == None:
            j.gui.dialog.askYesNo(" Do you want to link the dependencies?", False)
        if update == None:
            j.gui.dialog.askYesNo(" Do you want to update your code before exporting?", True)
        if update:
            self.codeUpdate(dependencies)
        if dependencies:
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.codeExport(update=update)
        self.actions.code_export()
        j.action.stop(False)

    def codeUpdate(self, dependencies=False, force=False):
        """
        Update code from code repo (get newest code)
        """
        self.loadActions()
        j.action.start('Update %s' % str(self), 'Failed to update code for %s' % str(self))
        j.clients.mercurial.statusClearAll()
        if dependencies:
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.codeUpdate(force=force)
        self.actions.code_update()
        j.action.stop(False)

    def codeCommit(self, dependencies=False, push=False):
        """
        update code from code repo (get newest code)
        """
        self.loadActions()
        j.action.start('Update %s' % str(self), 'Failed to update code for %s' % str(self))
        j.clients.mercurial.statusClearAll()
        if dependencies:
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.codeCommit(push=push)
        self.actions.code_commit()
        if push:
            self.codePush(dependencies)
        j.action.stop(False)

    def package(self, platform=j.enumerators.PlatformType.GENERIC, dependencies=False):
        """
        Package code from the sandbox system into files section of jpackages
        Only 1 platform may be supported in this jpackages at the same time!!!

        After the package action, the identities of the checked out commits of
        all repositories that were used in the recipe are saved to the
        jpackages.cfg file under the section 'repositories_PLATFORM'.

        @param platform: platform to package for
        @type platform: PlatformType
        @param dependencies: whether or not to package the dependencies
        @type dependencies: boolean
        """
        self.loadActions()
        if platform == None:
            raise RuntimeError("Cannot package because platform not specified")

        params = j.core.params.get()
        params.jpackages = self
        params.platform = platform
        j.action.start('Package %s' % str(self), 'Failed to package code for %s back to jpackages files section.' % str(self))
        # Disable action caching:
        # If a user packages for 2 different platforms in the same qshell
        # instance, the second call is just ignored, which is not desired
        # behaviour.
        # Also, when a user packages once, then sees a need to update his/her
        # code, and then packages again in the same qshell, again the second
        # time would be a non-op, which is again not desired. So we disable the
        # action caching for this action.
        if dependencies:
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.package(platform=platform)
        recipe = self.actions.code_getRecipe()
        self.actions.code_update()
        identities = recipe.identify()
        self.setIdentities(platform, identities)
        self.actions.code_package(platform=platform)
        j.action.stop(False)

    def setIdentities(self, platform, identifies):
        hrd = self.hrd.getHrd().getHRD('qp.name')
        for repokey, revision in identifies.iteritems():
            hrdkey = "qp.repositories.%s.%s" % (platform, repokey)
            hrd.set(hrdkey, revision)

    def compile(self,dependencies=False):
        self.loadActions()
        params = j.core.params.get()
        params.jpackages = self
        j.action.start('Compiling %s' % str(self))
        if dependencies:
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.compile()
        self.actions.compile()
        j.action.stop(False)

    @property
    def identities(self):
        """
        Identities of the commits this Q-Package was packaged from, by platform
        """
        cfg = self._getConfig()
        return cfg.getIdentities()

    def getBlobInfo(self):
        """
        Get information about the blobs of this Q-Package

        For each platform that has a blob, the BlobMetadata for that platform will be returned.

        If this package still has the legacy 'blob.info', the platform will be
        named 'blob', with the parsed blob.info file as value.

        @return: information about the blobs of this Q-Package
        @rtype: dict(PlatformType, BlobStor.BlobMetadata)
        """
        info = {}
        for platform in self.getBundlePlatforms():
            path = self._getBlobInfoPath(platform)
            if j.system.fs.isFile(path):
                description = j.clients.blobstor.parse(path)
                info[platform] = description
        legacyBlobPath = j.system.fs.joinPaths(self.metadataPath,
                "blob.info")
        if j.system.fs.isFile(legacyBlobPath):
            info['blob'] = j.clients.blobstor.parse(legacyBlobPath)
        return info

    def _getBlobInfoPath(self, platform):
        return j.system.fs.joinPaths(self.metadataPath, "blob_%s.info"%platform)

    def getBuilds(self, qualitylevels):
        """
        Get build information for the argument quality levels.

        The build information will be like this:
        [
            {
                "build_nr": 42,
                "identities": <identity information>,
                "quality_level": 'unstable',
                "node": '2ebf20ee306ddd97783c6476b9a903ae2171785b'
            },
            {
                "build_nr": 43,
                "identities": <identity information>,
                "quality_level": 'unstable',
                "node": '5572ac5c5db49534def6a579c0e94db175e478de'
            },
            {
                "build_nr": 42,
                "identities": <identity information>,
                "quality_level": 'testing',
                "node": '5242fe4e393acf9a613d12994a99962e4882a109'
            },
            ...
        ]

        The node value is the ID of the Mercurial commit in which the metadata
        was updated.

        @param qualitylevels: quality levels for the domain, in order
        @type qualitylevels:
        @return: build information for the argument quality levels
        @rtype: list(dict(string, object))
        """
        if not qualitylevels:
            raise ValueError("At least one quality level is required")

        def getInfo(ql, cfg):
            identities = cfg.getIdentities()
            buildNr = cfg.getBuildNumber()
            return {
                BUILD_NR: buildNr,
                QUALITY_LEVEL: ql,
                IDENTITIES: identities,
                }

        result = []
        unstableQualitylevel = qualitylevels[0]
        for nodeId, cfg in self._iterCfgHistory(unstableQualitylevel):
            info = getInfo(unstableQualitylevel, cfg)
            result.append(info)

        for ql in qualitylevels[1:]:
            path = self._getConfigPath(ql)
            if not j.system.fs.isFile(path):
                continue

            with open(path) as f:
                cfg = j.packages.jumpscale.pm_getJPackageConfig(f)
                buildNr = cfg.getBuildNumber()

            for r in result:
                if r[BUILD_NR] <= buildNr:
                    r[QUALITY_LEVEL] = ql
        return result

    def _iterCfgHistory(self, qualitylevel):
        """
        Iterate the history of the configuration file of this Q-Package on
        `qualitylevel`. For each JPackageConfig object, yield the node ID the
        configuration file version was committed on, and the JPackageConfig
        instance.

        Iterators are *NOT* supposed to edit the JPackageConfig file! This
        iterator is for read-only purposes.

        Also, the config file can only be used during the iteration step it is
        yielded!

        @param qualitylevel: quality level of the config file
        @type qualitylevel: string
        @return: iterator
        @rtype: iterator
        """
        domain = self._getDomainObject()
        hgc = domain.mercurialclient

        subPath = self._getCfgSubPath(qualitylevel)
        nodeIds = hgc.getFileChangeNodes(subPath)

        for nodeId in nodeIds:
            content = hgc.cat(nodeId, subPath)
            with contextlib.closing(StringIO(content)) as f:
                cfg = j.packages.jumpscale.pm_getJPackageConfig(f)
                yield nodeId, cfg

    def _getCfgSubPath(self, qualitylevel):
        """
        Get the path of the jpackages.cfg file for this Q-Package on the argument
        qualitylevel. The returned path will be relative the the metadata
        repository root.

        @param qualitylevel: qualitylevel the package should be on
        @type qualitylevel: string
        @return: path of the jpackages.cfg file for `qualitylevel`
        @rtype: string
        """
        return j.system.fs.joinPaths(qualitylevel, self.name,
                self.version, JPACKAGE_CFG)

    def codeImport(self, dependencies=False):
        """
        Import code back from system to local repo

        WARNING: As we cannot be sure where this code comes from, all identity
        information will be removed when this method is used!
        """
        self.loadActions()
        j.action.start('Import %s' % str(self), 'Failed to import code for %s back to local repo' % str(self))
        if dependencies:
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.codeImport()
        self.actions.code_importt()
        cfg = self._getConfig()
        cfg.clearIdentities(write=True)
        j.action.stop(False)

    def codePush(self, dependencies=False, merge=True):
        """
        Push code to repo (be careful this can brake code of other people)
        """
        self.loadActions()
        j.action.start('Push %s' % str(self), 'Failed to push code for %s' % str(self))
        j.clients.mercurial.statusClearAll()
        if dependencies:
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.codePush(merge=merge)
        self.actions.code_push(merge=merge)
        j.action.stop(False)

    def codeLink(self, dependencies=None, update=None, force=False):
        """
        Link code from local repo to right locations in sandbox

        @param force: if True, do an update which removes the changes (when using as install method should be True)
        """
        self.loadActions()
        j.clients.mercurial.statusClearAll()

        if dependencies is None:
            dependencies = j.gui.dialog.askYesNo("Do you want to link the dependencies?", False)

        if update is None:
            update = j.gui.dialog.askYesNo("Do you want to update your code before linking?", True)

        if update:
            self.codeUpdate(dependencies, force=force)
        if dependencies:
            deps = self.getDependencies(platform=j.system.platformtype)
            for dep in deps:
                dep.codeLink(update=update,force=force)            

        self.actions.code_push(force=force)
        j.action.stop(False)

    def download(self, dependencies=False, destinationDirectory=None, suppressErrors=False, allplatforms=False,expand=True):
        """
        Download the jpackages & expand
        Download the required blobs as well (as defined in qpackge.cfg dir)

        [requiredblobs]
        blob1= ...

        #param destinationDirectory: allows you to overwrite the default destination (opt/qbase/var/jpackages/files/...)
        """
        self.loadActions()
        j.action.start('Downloading %s' % str(self), 'Failed to download %s' % str(self))
        if dependencies:
            deps = self.getDependencies(recursive=True)
            for dep in deps:
                dep.download(dependencies=False, destinationDirectory=destinationDirectory,allplatforms=allplatforms,expand=expand)

        j.packages.jumpscale.getDomainObject(self.domain)

        self._log('Downloading bundles for package ' + str(self))
        state = self.getState()

        downloadDestinationDirectory = destinationDirectory

        try:
            j.system.fs.removeDirTree(self.getPathFiles())
        except:
            pass
        j.system.fs.createDir(self.getPathFiles())

        for platform in self.getBundlePlatforms():
            
            checksum = self.getBundleKey(platform)
            self._log("bundle key found:%s for platform:%s"%(checksum,platform))
            if checksum == None:
                #no checksum found in config file, probably since it uses different platform
                continue

            if destinationDirectory == None:
                downloadDestinationDirectory = j.system.fs.joinPaths(self.getPathFiles(), str(platform))


            if state.downloadedBlobStorKeys.has_key(platform) and state.downloadedBlobStorKeys[platform] == checksum:
                j.console.echo("No need to download jpackages %s" % self.name)
                continue

            if not self.blobstorLocal.exists(checksum):
                self.blobstorRemote.copyToOtherBlocStor(checksum, self.blobstorLocal)

            if expand:
                self.blobstorLocal.download(checksum, downloadDestinationDirectory)

        #@todo need to check why this is needed
        # #download the required blobs
        # for checksum in self.requiredblobs.itervalues():
        #     self.blobstorRemote.copyToOtherBlocStor(checksum, self.blobstorLocal)

        j.action.stop(False)
        return True


    def getBundleKey(self,platform):
        platform=str(platform)
        if self.bundles.has_key(platform):
            return self.bundles[platform]
        else:
            return None

    # upload the bundle
    def upload(self, remote=True, local=True):
        """
        Upload jpackages to Blobstor, default remote and local
        """
        self._log('Begin Uploading bundles for package ' + str(self) + ' ... (Please wait)')
        self.loadActions()

        j.packages.jumpscale.getDomainObject(self.domain)

        updateBuildnr = False
        foundAnyPlatform = False
        #delete blob.info (not used anymore)
        if j.system.fs.exists(j.system.fs.joinPaths(self.metadataPath, "blob.info")):
            j.system.fs.removeFile(j.system.fs.joinPaths(self.metadataPath, "blob.info"))

        for platform in self.getBundlePlatforms():
            # self.getBundleKey(platform) #hash as stored in config file
            pathFilesForPlatform = self.getPathFilesPlatform(platform)

            foundAnyPlatform = True

            if not j.system.fs.exists(pathFilesForPlatform):
                path = self._getBlobInfoPath(platform)
                j.system.fs.removeFile(path)
                continue


            plchecksum = self.getBundleKey(platform)

            if local and remote and self.blobstorRemote <> None and self.blobstorLocal <> None:
                key, descr, uploadedAnything = self.blobstorLocal.put(pathFilesForPlatform, blobstores=[self.blobstorRemote], prevkey=plchecksum)
            elif local and self.blobstorLocal <> None:
                key, descr, uploadedAnything = self.blobstorLocal.put(pathFilesForPlatform, blobstores=[], prevkey=plchecksum)
            elif remote and self.blobstorRemote <> None:
                key, descr, uploadedAnything = self.blobstorRemote.put(pathFilesForPlatform, blobstores=[], prevkey=plchecksum)
            else:
                raise RuntimeError("need to upload to local or remote")
            print key

            if plchecksum <> key:
                j.console.echo("files did change for %s, upgrade buildnr" % self.name)
                updateBuildnr = True
                self.bundles[str(platform)] = key
                path = self._getBlobInfoPath(platform)
                j.system.fs.writeFile(path, descr)
                self.save()
                self._log('Successfully uploaded bundles for package ' + str(self) )
            else:
                j.console.echo("files did not change for %s, no need to upgrade buildnr for filechange" % self.name)

        taskletsChecksum, descr2 = j.tools.hash.hashDir(j.system.fs.joinPaths(self.metadataPath, "actions"))
        if taskletsChecksum <> self.taskletsChecksum:
            j.console.echo("actions did change for %s, upgrade buildnr" % self.name)
            #buildnr needs to go up
            updateBuildnr = True
            self.taskletsChecksum = taskletsChecksum
        else:
            j.console.echo("actions did not change for %s, no need to upgrade buildnr for taskletchange" % self.name)

        if  updateBuildnr:
            self.buildNr += 1
            self.save()

        if foundAnyPlatform == False:
            self._log('No platform found for upload' )
            j.console.echo("No platform found for upload")
            
            
        self.load()



#    def _copyFilesToSandbox(self):          #Todo: function still being used???
#        ##
#        ##Copy Files from package dir to sandbox
#        ##@param dirName: name of the directory to copy
#        ##
#        _jpackagesDir = self.getPathFiles()
#
#        j.logger.log('Syncing %s to sandbox' % _jpackagesDir, 5)
#        platformDirsToCopy = self._getPlatformDirsToCopy()
#        print 'platformDirsToCopy: ' + str(platformDirsToCopy)
#        if False:
#            try:
#                t = 1/0
#            except:
#                import traceback
#                print '\n'.join(traceback.format_stack())
#        for platformDir in platformDirsToCopy:
#            j.logger.log('Syncing files in <%s>'%platformDir, 5)
#            self._copyFilesTo(platformDir, j.dirs.baseDir)
    def _getPlatformDirsToCopy(self):
        """
        Return a list of platform related directories to be copied in sandbox
        """

        platformDirs = list()
        platform = j.system.platformtype

        _jpackagesDir = self.getPathFiles()

        platformSpecificDir = j.system.fs.joinPaths(_jpackagesDir, str(platform), '')

        if j.system.fs.isDir(platformSpecificDir):
            platformDirs.append(platformSpecificDir)

        genericDir = j.system.fs.joinPaths(_jpackagesDir, 'generic', '')

        if j.system.fs.isDir(genericDir):
            platformDirs.append(genericDir)

        if platform.isUnix():
            unixDir = j.system.fs.joinPaths(_jpackagesDir, 'unix', '')
            if j.system.fs.isDir(unixDir):
                platformDirs.append(unixDir)

            if platform.isSolaris():
                sourceDir = j.system.fs.joinPaths(_jpackagesDir, 'solaris', '')
            elif platform.isLinux():
                sourceDir = j.system.fs.joinPaths(_jpackagesDir, 'linux', '')
            elif platform.isDarwin():
                sourceDir = j.system.fs.joinPaths(_jpackagesDir, 'darwin', '')

        elif platform.isWindows():
            sourceDir = j.system.fs.joinPaths(_jpackagesDir, 'win', '')

        if j.system.fs.isDir(sourceDir):
            if not str(sourceDir) in platformDirs:
                platformDirs.append(sourceDir)

        return platformDirs


########################################################################
#########################  RECONFIGURE  ################################
########################################################################

    def signalConfigurationNeeded(self):
        """
        Set in the corresponding jpackages's state file if reconfiguration is needed
        """
        self.getState().setIsPendingReconfiguration(True)
        j.packages.jumpscale._setHasPackagesPendingConfiguration(True)

    def isPendingReconfiguration(self):
        """
        Check if the JPackage needs reconfiguration
        """
        if self.getState().getIsPendingReconfiguration() == 1:
            return True
        return False

#############################################################################
###############################  TASKLETS  ##################################
#############################################################################

    def executeAction(self, action, tags, dependencies=False, params=None,
            actionCaching=True):
        """
        Execute tasklets of specific jpackages

        @param action is "install", "codeManagement","configure","package","backup", ...
        @param actionCaching: can be used to disable the action caching
        @type actionCaching: boolean
        """
        if actionCaching:
            if j.packages.jumpscale._actionCheck(self, action):
                return True

            j.packages.jumpscale._actionSet(self, action)

        #process all dependencies
        state = self.getState()
        if dependencies:
            deps = self.getDependencies(recursive=True)
            for dep in deps:
                dep.executeAction(action,tags,  dependencies,params=params)
        state = self.getState()
        self._log('executing jpackages action ' + tags + ' ' + action)
        state.setCurrentAction(tags, action)
        self.actions.execute(action, tags=tags, params=params) #tags are not used today
        self.getState().setCurrentActionIsDone()


#########################################################################
#######################  SUPPORTING FUNCTIONS  ##########################

    def _getDomainObject(self):
        """
        Get the domain object for this Q-Package

        @return: domain object for this Q-Package
        @rtype: Domain.Domain
        """
        return j.packages.jumpscale.getDomainObject(self.domain)

    def _raiseError(self,message):
        ##self.assertAccessable()
        message = "%s : %s_%s_%s" % (message, self.domain, self.name, self.version)
        raise RuntimeError(message)

    def _clear(self):
        ##self.assertAccessable()
        """
        Clear all properties except domain, name, and version
        """
        self.tags = []
        self.supportedPlatforms = []
        self.buildNr = 0
        self.dependencies = []

    def __cmp__(self,other):
        if other == None or other=="":
            return False
        return self.name == other.name and str(self.domain) == str(other.domain) and j.packages.jumpscale._getVersionAsInt(self.version) == j.packages.jumpscale._getVersionAsInt(other.version)

    def __repr__(self):
        return self.__str__()

    def getInteractiveObject(self):
        """
        Return the interactive version of the jpackages object
        """
        ##self.assertAccessable()
        return JPackageIObject(self)

    def _resetPreparedForUpdatingFiles(self):
        self.getState().setPrepared(0)

    def __str__(self):
        return "JPackage %s %s %s" % (self.domain, self.name, self.version)

    def __eq__(self, other):
        return str(self) == str(other)

    def _log(self, mess):
        j.logger.log(str(self) + ':' + mess, 3)
        print str(self) + ':' + mess

    def reportNumbers(self):
        #return ' metaNr:' + str(self.metaNr) + ' bundleNr:' + str(self.bundleNr) + ' buildNr:' + str(self.buildNr)
        return ' buildNr:' + str(self.buildNr)
