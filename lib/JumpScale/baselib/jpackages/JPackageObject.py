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
from JumpScale.core.baseclasses.dirtyflaggingmixin import DirtyFlaggingMixin
from JPackageStateObject import JPackageStateObject
#from JumpScale.core.sync.Sync import SyncLocal
from ActionManager import ActionManager

JPACKAGE_CFG = "jpackages.cfg"
BUILD_NR = "build_nr"
QUALITY_LEVEL = "quality_level"
IDENTITIES = "identities"

class DependencyDef():
    def __init__(self,name,domain,minversion=None,maxversion=None):
        self.name=name
        self.domain=domain
        self.minversion=minversion
        self.maxversion=maxversion

    def __str__(sel):
        return str(self.__dict__)

    __repr__=__str__


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
        
        self.configchanged=False

        self.metadataPath=self.getPathMetadata()
        
        self.description=""
        
        self.metadata=None
                
        self.__init=False

        self._init()

    def log(self,msg,category="",level=5):
        if level<j.packages.loglevel+1 and j.packages.logenable:
            j.packages.log("%s:%s"%(self,msg),category=category,level=level)        

    def check(self):
        if not self.supportsPlatform():
            raise RuntimeError("Only those platforms are supported by this package %s your system supports the following platforms: %s" % (str(self.supportedPlatforms), str(j.system.platformtype.getMyRelevantPlatforms())))

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
        
        self.hrd=j.core.hrd.getHRD(path=j.system.fs.joinPaths(hrddir,"main.hrd"))

        if self.hrd.get("qp.domain",checkExists=True)<>self.domain:
            self.hrd.set("qp.domain",self.domain)
        if self.hrd.get("qp.name",checkExists=True)<>self.name:
            self.hrd.set("qp.name",self.name)
        if self.hrd.get("qp.version",checkExists=True)<>self.version:                
            self.hrd.set("qp.version",self.version)    
        
        descr=self.hrd.get("qp.description",checkExists=True)
        if descr<>False and descr<>"":
            self.description=descr
        if descr<>self.description:                
            self.hrd.set("qp.description",self.description)                      

        self.supportedPlatforms=self.hrd.getList("qp.supportedplatforms")

        for platform in self.supportedPlatforms:
            j.system.fs.createDir(self.getPathFilesPlatform(platform))        


    def load(self,hrdDir=None,position=""):                

        #create defaults for new jpackages
        hrddir=j.system.fs.joinPaths(self.metadataPath,"hrd")
        if not j.system.fs.exists(hrddir):  
            self.init()
        self.hrd=j.core.hrd.getHRD(hrddir)
        self._clear()
        self.buildNr = self.hrd.getInt("qp.buildnr")
        self.export = self.hrd.getBool("qp.export")
        self.autobuild = self.hrd.getBool("qp.autobuild")
        self.taskletsChecksum = self.hrd.get("qp.taskletschecksum")
        try:
            self.descrChecksum = self.hrd.get("qp.descrchecksum")
        except:
            hrd = self.hrd.getHrd("").getHRD("qp.name")
            hrd.set("qp.descrchecksum","")
            self.descrChecksum = self.hrd.get("qp.descrchecksum")
        try:
            self.hrdChecksum = self.hrd.get("qp.hrdchecksum")
        except:
            hrd = self.hrd.getHrd("").getHRD("qp.name")
            hrd.set("qp.hrdchecksum","")
            self.hrdChecksum = self.hrd.get("qp.hrdchecksum")

        self.supportedPlatforms = self.hrd.getList("qp.supportedplatforms")
        self.bundles = self.hrd.getDict("qp.bundles") #dict with key platformkey and val the hash of bundle
        
        j.packages.getDomainObject(self.domain)

        self.blobstorRemote = None
        self.blobstorLocal = None

        self.actions = None

        self._getState()        

        self.debug=self.state.debugMode

        # 

    def _loadActiveHrd(self):
        """
        match hrd templates with active ones, add entries where needed
        """
        hrdtemplatesPath=j.system.fs.joinPaths(self.metadataPath,"hrdactive")
        for item in j.system.fs.listFilesInDir(hrdtemplatesPath):
            base=j.system.fs.getBaseName(item)
            if base[0]<>"_":
                templ=j.system.fs.fileGetContents(item)                
                actbasepath=j.system.fs.joinPaths(j.dirs.hrdDir,base)
                if not j.system.fs.exists(actbasepath):
                    #means there is no hrd, put empty file
                    self.log("did not find active hrd for %s, will now put there"%actbasepath,category="init")
                    j.system.fs.writeFile(actbasepath,"")
                hrd=j.core.hrd.getHRD(actbasepath)
                hrd.checkValidity(templ)
                if hrd.changed:
                    #a configure change has happened
                    self.configchanged=True
                    #also needs to reload the config object on the application object
                    j.application.initWhoAmI() #will load that underneath


    def loadActions(self, force=False):
        if self.actions <> None and not force:
            return

        self.check()

        self._loadActiveHrd()

        j.system.fs.copyDirTree(j.system.fs.joinPaths(self.metadataPath,"actions"),self.getPathActions())        
        
        #apply apackage hrd data on actions active
        self.hrd.applyOnDir(self.getPathActions()) #make sure params are filled in in actions dir
        #apply hrd configu from system on actions active
        j.application.config.applyOnDir(self.getPathActions())

        self.actions = ActionManager(self)
        
        do = j.packages.getDomainObject(self.domain)
        if do.blobstorremote.strip() <> "":
            self.blobstorRemote = j.clients.blobstor.get(do.blobstorremote)

        if do.blobstorlocal.strip() <> "":
            self.blobstorLocal = j.clients.blobstor.get(do.blobstorlocal)

    def getDebugMode(self):
        return self.state.debugMode

    def setDebugMode(self):
        self.state.setDebugMode()
        self.log("set debug mode",category="init")

    def removeDebugMode(self):
        self.state.setDebugMode(mode=0)
        self.log("remove debug mode",category="init")


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
            path = j.packages.getDataPath(self.domain, self.name, self.version)
            j.system.fs.removeDirTree(path)
            path = j.packages.getMetadataPath(self.domain, self.name,self.version)
            j.system.fs.removeDirTree(path)
            path = j.packages.getQPActionsPath(self.domain, self.name,self.version)
            j.system.fs.removeDirTree(path)
            for f in j.system.fs.listFilesInDir(j.packages.getBundlesPath()):
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
        self.log('saving jpackages data to ' + self.metadataPath,category="save")

        if self.buildNr == "":
            self._raiseError("buildNr cannot be empty")

        self.hrd.set("qp.buildnr",self.buildNr)        
        self.hrd.set("qp.export",self.export)
        self.hrd.set("qp.autobuild",self.autobuild)
        self.hrd.set("qp.taskletschecksum",self.taskletsChecksum)
        self.hrd.set("qp.hrdchecksum",self.hrdChecksum)
        self.hrd.set("qp.descrchecksum",self.descrChecksum)
        self.hrd.set("qp.supportedplatforms",self.supportedPlatforms)
        self.hrd.set("qp.bundles",self.bundles)

        for idx, dependency in enumerate(self.dependencies):
            self._addDependencyToHRD(idx, dependency.domain, dependency.name,minversion=dependency.minversion,maxversion=dependency.maxversion)

    def _addDependencyToHRD(self, idx, domain, name, minversion, maxversion):
        hrd = self.hrd
        basekey = 'qp.dependency.%s.%%s' % idx
        def setValue(name, value):
            hrd.set(basekey % name, value)

        setValue('domain', domain)
        setValue('name', name)
        setValue('minversion', minversion)
        setValue('maxversion', maxversion)


##################################################################################################
###################################  CONFIG FILE HANDLING  #######################################
##################################################################################################


    def loadDependencies(self):
        if self.dependencies==[]:
            self.dependencyDefs = []

            addedstuff = set()
            for key in self.hrd.prefix('qp.dependency'):
                parts = key.split('.')
                if parts[2] in addedstuff:
                    continue
                key = "%s.%%s" % (".".join(parts[:3]))

                if not self.hrd.exists(key % 'minversion'):
                    self.hrd.set(key % 'minversion',"")
                if not self.hrd.exists(key % 'maxversion'):
                    self.hrd.set(key % 'maxversion',"")
                   
                dependencyDef=DependencyDef(self.hrd.get(key % 'name'),
                    self.hrd.get(key % 'domain'),
                    self.hrd.get(key % 'minversion'),
                    self.hrd.get(key % 'maxversion'))

                addedstuff.add(parts[2])
                self.dependencyDefs.append(dependencyDef)

            for dependcyDef in self.dependencyDefs:

                package=j.packages.findNewest(dependcyDef.domain,dependcyDef.name,\
                    minversion=dependencyDef.minversion,maxversion=dependencyDef.maxversion,platform=j.system.platformtype.myplatform)

                if package not in self.dependencies:
                    self.dependencies.append(package)

                for deppack in package.getDependencies():
                    if deppack not in self.dependencies:
                        self.dependencies.append(deppack)                
        
    def addDependency(self, domain, name, supportedplatforms, minversion, maxversion, dependencytype):
        dep = DependencyDef4()
        dep.name = name
        dep.domain = domain
        dep.minversion = minversion
        dep.maxversion = maxversion
        # dep.supportedPlatforms = supportedplatforms
        # dep.dependencytype = j.enumerators.DependencyType4.getByName(dependencytype)
        self.dependencyDefs.append(dep)
        self.save()
        self.dependencies=[]
        self.loadDependencies()
        

#############################################################################
####################################  GETS  #################################
#############################################################################

    def getIsPreparedForUpdatingFiles(self):
        """
        Return true if package has been prepared
        """
        prepared = self.state.prepared
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

    def getDependingPackages(self, recursive=False):
        """
        Return the packages that are dependent on this package
        This is a heavy operation and might take some time
        """
        return [p for p in j.packages.getJPackageObjects() if self in p.getDependencies()]


    def _getState(self):
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
        self.state=JPackageStateObject(self)

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
        return j.packages.getQPActionsPath(self.domain, self.name, self.version)

    def getPathMetadata(self):
        """
        Return absolute pathname of the package's metadatapath active
        """
        return j.packages.getMetadataPath(self.domain, self.name, self.version)


    def getPathFiles(self):
        """
        Return absolute pathname of the jpackages's filespath
        """
        ##self.assertAccessable()
        return j.packages.getDataPath(self.domain, self.name, self.version)


    def getPathFilesPlatform(self, platform=None):
        """
        Return absolute pathname of the jpackages's filespath
        if not given then will be: j.system.platformtype
        """
        ##self.assertAccessable()
        if platform==None:
            platform=j.system.platformtype.myplatform
        platform=self._getPackageInteractive(platform)
        path =  j.system.fs.joinPaths(self.getPathFiles(), str(platform))
        return path

    def getPathFilesPlatformForSubDir(self, subdir):
        """
        Return absolute pathnames of the jpackages's filespath for platform or parent of platform if it does not exist in lowest level
        if platform not given then will be: j.system.platformtype
        the subdir will be used to check upon if found in one of the dirs, if never found will raise error
        all matching results are returned
        """
        result=[]
        for possibleplatform in j.system.platformtype.getMyRelevantPlatforms():
            # print platform
            path =  j.system.fs.joinPaths(self.getPathFiles(), possibleplatform,subdir)
            #print path
            if j.system.fs.exists(path):
                result.append(path)
        if len(result)==0:
            raise RuntimeError("Could not find subdir %s in files dirs for '%s'"%(subdir,self))
        return result

    def copyPythonLibs(self,remove=False):
        """
        will look in platform dirs of qpackage to find "site-packages" dir (starting from lowest platform type e.g. linux64, then parents of platform)
        each dir "site-packages" found in one of the site-packages dir will be copied to the local site packages dir
        """
        # j.system.platform.python.getSitePackagePathLocal
        for path in self.getPathFilesPlatformForSubDir("site-packages"):
            # self.log("copy python lib to %s"%path,category="libinstall")
            self.log("Copy python lib:%s to site packages"%path,category="copylib")
            j.system.platform.python.copyLibsToLocalSitePackagesDir(path,remove=remove)


    def installUbuntuDebs(self):
        for path in self.getPathFilesPlatformForSubDir("debs"):
            for item in j.system.fs.listFilesInDir(path,filter="*.deb"):
                j.system.platform.ubuntu.installDebFile(item)            

    def getPathSourceCode(self):
        """
        Return absolute path to where this package's source can be extracted to
        """
        raise NotImplementedError()
        #return j.system.fs.joinPaths(j.dirs.varDir, 'src', self.name, self.version)

    def getHighestInstalledBuildNr(self):
        """
        Return the latetst installed buildnumber
        """
        ##self.assertAccessable()
        return self.state.lastinstalledbuildnr



    def getBrokenDependencies(self, platform=None):
        """
        Return a list of dependencies that cannot be resolved
        """
        platform=self._getPackageInteractive(platform)
        broken = []
        for dep in self.dependencies:   # go over my dependencies
                                        # Do this without try catch
                                        # pass boolean to findnewest that it should return None instead of fail
            try:
                j.packages.findNewest(domain=dep.domain, name=dep.name, minversion=dep.minversion, maxversion=dep.maxversion, platform=platform)
            except Exception, e:
                print str(e)
                broken.append(dep)
        return broken




    def getDependencyTree(self, platform=None):
        """
        Return the dependencies for the JPackage

        @param platform see j.system.platformtype....        
        """
        self.loadDependencies()
        platform=self._getPackageInteractive(platform)
        self.pm_getDependencies(None, platform, recursive=True, printTree=True)


    def getDependencies(self):
        """
        Return the dependencies for the JPackage
        """
        self.loadDependencies()
        return self.dependencies

#############################################################################
################################  CHECKS  ###################################
#############################################################################

    def hasModifiedFiles(self):
        """
        Check if files are modified in the JPackage files
        """
        ##self.assertAccessable()
        if self.state.prepared == 1:
            return True
        return False

    def hasModifiedMetaData(self):
        """
        Check if files are modified in the JPackage metadata
        """
        ##self.assertAccessable()
        return self in j.packages.getDomainObject(self.domain).getJPackageTuplesWithModifiedMetadata()

    def isInstalled(self):
        """
        Check if the JPackage is installed
        """
        ##self.assertAccessable()
        return self.state.lastinstalledbuildnr != -1

    def supportsPlatform(self,platform=None):
        """
        Check if a JPackage can be installed on a platform
        """
        if platform==None:
            relevant=j.system.platformtype.getMyRelevantPlatforms()
        else:
            relevant=j.system.platformtype.getParents(platform)
        for supportedPlatform in self.supportedPlatforms:
            if supportedPlatform in relevant:
                return True
        return False

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
        self.log('export to %s '%(url))

    def importt(self, url):
        """
        Restore a backup, run, the restore tasklet(s)

        @param url: location of the backup, e.g. : ftp://login:passwd@10.10.1.1/myroot/
        """
        
        self.actions.importt(url=url)
        self.log('import from %s '%(url))

    def start(self):
        """
        Start the JPackage, run the start tasklet(s)
        """
        
        self.actions.start()
        self.log('start')

    def stop(self):
        """
        Stop the JPackage, run the stop tasklet(s)
        """
        
        self.actions.stop()
        self.log('stop')


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
        self.log('isrunning')


    def _isHostPlatformSupported(self, platform):
        '''
        Checks if a given platform is supported, the checks takes the
        supported platform their parents in account.

        @param platform: platform to check
        @type platform: j.system.platformtype

        @return: flag that indicates if the given platform is supported
        @rtype: Boolean
        '''

        #@todo P1 no longer working use new j.system.platformtype

        supportedPlatformPool = list()

        for platform in self.supportedPlatforms:
            while platform != None:
                supportedPlatformPool.append(platform)
                platform = platform.parent

        if platform in supportedPlatformPool:
            return True
        else:
            return False


    def reinstall(self, dependencies=False, download=True):
        """
        Reinstall the JPackage by running its install tasklet, best not to use dependancies reinstall 
        """        
        self.install(dependencies=dependencies, download=download, reinstall=True)

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

        if j.packages._actionCheck(self,action):
            return True


        # If I am already installed assume my dependencies are also installed
        if self.buildNr <> -1 and self.buildNr <= self.state.lastinstalledbuildnr and not reinstall:
            self.log('already installed')
            return # Nothing to do

        if dependencies:            
            deps = self.getDependencies()
            for dep in deps:
                dep.install(dependencies, download, reinstall)
            self.loadActions(True) #reload actions to make sure new hrdactive are applied

        action = "install"
        if download and self.debug <> True:
            self.download(dependencies=False)

        if reinstall or self.buildNr > self.state.lastinstalledbuildnr:
            
            if self.debug == False:
                #print 'really installing ' + str(self)
                self.log('installing')
                if self.state.checkNoCurrentAction == False:
                    raise RuntimeError ("jpackages is in inconsistent state, ...")                

                self.actions.install()
                self.state.setLastInstalledBuildNr(self.buildNr)
            else:
                #only the link functionality for now
                self.log('install for debug (link)')
                self.codeLink(dependencies=dependencies, update=True, force=True)

        if self.buildNr==-1 or self.configchanged or reinstall or self.buildNr >= self.state.lastinstalledbuildnr:
            self.configure()


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
        state = self.state
        if state.checkNoCurrentAction == False:
            raise RuntimeError ("jpackages is in inconsistent state, ...")
        self.log('uninstalling' + str(self))
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
        if  self.state.prepared <> 1:
            if not self.isNew():
                self.download(suppressErrors=suppressErrors)
                self._expand(suppressErrors=suppressErrors)
            self.state.setPrepared(1)

    def isNew(self):
        # We are new when our files have not yet been committed
        # check if our jpackages.cfg file in the repo is in the ignored or added categories
        domainObject = self._getDomainObject()
        cfgPath = j.system.fs.joinPaths(self.metadataPath, JPACKAGE_CFG)
        return not domainObject._isTrackingFile(cfgPath)

    def copyFiles(self, subdir="",destination="",applyhrd=False):
        """
        Copy the files from package dirs (/opt/qbase5/var/jpackages/...) to their proper location in the sandbox.

        @param destination: destination of the files, default is the sandbox
        """

        if destination=="":
            raise RuntimeError("A destination needs to be specified.") #done for safety, jpackages have to be adjusted

        for path in self.getPathFilesPlatformForSubDir(subdir):
            # self.log("copy python lib to %s"%path,category="libinstall")
            self.log("Copy files from %s to %s"%(path,destination),category="copy")

            if applyhrd:
                tmpdir=j.system.fs.getTmpDirPath()
                j.system.fs.copyDirTree(path,tmpdir)
                j.application.config.applyOnDir(tmpdir)
                self._copyFilesTo(tmpdir, destination)
                j.system.fs.removeDirTree(tmpdir)
            else:
                self._copyFilesTo(path, destination)
                


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
        prefixHiddenFile = sourceDir + '.hg'

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
                    self.log("Copying <%s>" % destinationFile)

                    createAncestors(destinationFile)
                    if j.system.fs.isLink( file ) :
                        j.system.fs.symlink(os.readlink( file ), destinationFile, overwriteTarget=True )
                    elif j.system.fs.isDir (file) :
                        j.system.fs.createDir(destinationFile )
                    else:
                        j.system.fs.copyFile(file, destinationFile)

            self.log('Syncing done')
        else:
            self.log('Directory <%s> does not exist' % sourceDir)

    def configure(self, dependencies=False):
        """
        Configure the JPackage after installation, via the configure tasklet(s)
        """
        self.log('configure')
        
        self.loadActions()
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.configure()
        self.actions.configure()
        # self.state.setIsPendingReconfiguration(False)
        j.application.initWhoAmI() #makes sure hrd gets reloaded to application.config object

    def codeExport(self, dependencies=False, update=None):
        """
        Export code to right locations in sandbox or on system
        code recipe is being used
        only the sections in the recipe which are relevant to you will be used
        """
        
        self.loadActions()
        self.log('CodeExport')
        if dependencies == None:
            j.gui.dialog.askYesNo(" Do you want to link the dependencies?", False)
        if update == None:
            j.gui.dialog.askYesNo(" Do you want to update your code before exporting?", True)
        if update:
            self.codeUpdate(dependencies)
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.codeExport(update=update)
        self.actions.code_export()

    def codeUpdate(self, dependencies=False, force=False):
        """
        Update code from code repo (get newest code)
        """
        self.log('CodeUpdate')
        self.loadActions()
        # j.clients.mercurial.statusClearAll()
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.codeUpdate(force=force)
        self.actions.code_update()

    def codeCommit(self, dependencies=False, push=False):
        """
        update code from code repo (get newest code)
        """
        
        self.loadActions()
        self.log('CodeCommit')
        j.clients.mercurial.statusClearAll()
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.codeCommit(push=push)
        self.actions.code_commit()
        if push:
            self.codePush(dependencies)


    def _getPackageInteractive(self,platform):

        if platform == None and len(self.supportedPlatforms) == 1:
            platform = self.supportedPlatforms[0]
        
        if platform==None and j.application.shellconfig.interactive:
            platform = j.gui.dialog.askChoice("Select platform.",self.supportedPlatforms ,str(None))
        
        if platform==None:
            platform=None
        return platform

    
    def build(self, platform=None, dependencies=False):
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
        

        platform=self._getPackageInteractive(platform)
        
        self.loadActions()

        params = j.core.params.get()
        params.jpackages = self
        params.platform = platform
        self.log('Package')
        # Disable action caching:
        # If a user packages for 2 different platforms in the same qshell
        # instance, the second call is just ignored, which is not desired
        # behaviour.
        # Also, when a user packages once, then sees a need to update his/her
        # code, and then packages again in the same qshell, again the second
        # time would be a non-op, which is again not desired. So we disable the
        # action caching for this action.
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.package(platform=platform)
        recipe = self.actions.code_getRecipe()
        self.actions.code_update()
        identities = recipe.identify()
        self.setIdentities(platform, identities)
        self.actions.code_package(platform=platform)

    def setIdentities(self, platform, identifies):

        platform=self._getPackageInteractive(platform)

        hrd = self.hrd.getHrd().getHRD('qp.name')
        for repokey, revision in identifies.iteritems():
            hrdkey = "qp.repositories.%s.%s" % (platform, repokey)
            hrd.set(hrdkey, revision)

    def compile(self,dependencies=False):
        
        self.loadActions()
        params = j.core.params.get()
        params.jpackages = self
        self.log('Compile')
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.compile()
        self.actions.compile()

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
        for platform in j.system.platformtype.getMyRelevantPlatforms() :
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
                cfg = j.packages.pm_getJPackageConfig(f)
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
                cfg = j.packages.pm_getJPackageConfig(f)
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
        j.log("CodeImport")
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.codeImport()
        self.actions.code_importt()
        cfg = self._getConfig()
        cfg.clearIdentities(write=True)

    def codePush(self, dependencies=False, merge=True):
        """
        Push code to repo (be careful this can brake code of other people)
        """
        
        self.loadActions()
        j.log("CodePush")
        j.clients.mercurial.statusClearAll()
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.codePush(merge=merge)
        self.actions.code_push(merge=merge)

    def codeLink(self, dependencies=None, update=None, force=False):
        """
        Link code from local repo to right locations in sandbox

        @param force: if True, do an update which removes the changes (when using as install method should be True)
        """
        
        self.loadActions()
        # j.clients.mercurial.statusClearAll()
        self.log("CodeLink")
        if dependencies is None:
            if j.application.shellconfig.interactive:
                dependencies = j.gui.dialog.askYesNo("Do you want to link the dependencies?", False)
            else:
                raise RuntimeError("Need to specify arg 'depencies' (true or false) when non interactive")


        if update is None:
            if j.application.shellconfig.interactive:
                update = j.gui.dialog.askYesNo("Do you want to update your code before linking?", True)
            else:
                raise RuntimeError("Need to specify arg 'update' (true or false) when non interactive")

        if update:
            self.codeUpdate(dependencies, force=force)
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.codeLink(update=update,force=force)            

        self.actions.code_link(force=force)
        # self.actions.code_push(force=force)  #@todo was this before, was pushing content


    def download(self, dependencies=None, destinationDirectory=None, suppressErrors=False, allplatforms=False,expand=True):
        """
        Download the jpackages & expand
        Download the required blobs as well (as defined in qpackge.cfg dir)

        [requiredblobs]
        blob1= ...

        #param destinationDirectory: allows you to overwrite the default destination (opt/qbase/var/jpackages/files/...)
        """

        if dependencies==None and j.application.shellconfig.interactive:
            dependencies = j.console.askYesNo("Do you want the bundles of all depending packages to be downloaded too?")
        else:
            dependencies=True
        
        self.loadActions()
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.download(dependencies=False, destinationDirectory=destinationDirectory,allplatforms=allplatforms,expand=expand)

        j.packages.getDomainObject(self.domain)

        self.log('Downloading bundles.')

        downloadDestinationDirectory = destinationDirectory

        for platform in j.system.platformtype.getMyRelevantPlatforms():
            
            checksum = self.getBundleKey(platform)
            
            if checksum == None:
                #no checksum found in config file, probably since it uses different platform
                continue

            self.log("bundle key found:%s for platform:%s"%(checksum,platform),category="download",level=6)

            if destinationDirectory == None:
                downloadDestinationDirectory = j.system.fs.joinPaths(self.getPathFiles(), str(platform))
            
            if self.state.downloadedBlobStorKeys.has_key(platform) and self.state.downloadedBlobStorKeys[platform] == checksum:
                self.log("No need to download/expand for platform '%s', already there."%platform,level=5)
                continue

            if not self.blobstorLocal.exists(checksum):
                self.blobstorRemote.copyToOtherBlobStor(checksum, self.blobstorLocal)

            if expand:
                self.log("expand platform:%s"%platform,category="download")
                j.system.fs.removeDirTree(downloadDestinationDirectory)
                j.system.fs.createDir(downloadDestinationDirectory)
                self.blobstorLocal.download(checksum, downloadDestinationDirectory)
                self.state.downloadedBlobStorKeys[platform] = checksum
                self.state.save()

        #@todo need to check why this is needed
        # #download the required blobs
        # for checksum in self.requiredblobs.itervalues():
        #     self.blobstorRemote.copyToOtherBlobStor(checksum, self.blobstorLocal)

        return True


    def getBundleKey(self,platform):
        platform=str(platform)
        if self.bundles.has_key(platform):
            if self.bundles[platform]=="":
                return None
            return self.bundles[platform]
        else:
            return None


    def backup(self,url=None,dependencies=False):
        """
        Make a backup for this package by running its backup tasklet.
        """
        
        if url==None:
            url = j.console.askString("Url to backup to?")
        else:
            raise RuntimeError("url needs to be specified")

        self.loadActions()
        params = j.core.params.get()
        params.jpackages = self
        params.url=url
        self.log('Backup')
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.backup(url=url)
        self.actions.backup()

    def restore(self,url=None,dependencies=False):
        """
        Make a restore for this package by running its restore tasklet.
        """
        
        if url==None:
            url = j.console.askString("Url to restore to?")
        else:
            raise RuntimeError("url needs to be specified")
        self.log('restore')
        self.loadActions()
        params = j.core.params.get()
        params.jpackages = self
        params.url=url
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.restore(url=url)
        self.actions.restore()        

    def buildupload(self, platform=None):
        self.package(platform)
        self.upload()

    def getBundleDirs(self):
        result=[]
        for platform in j.system.platformtype.getMyRelevantPlatforms():
            if platform=="":
                continue            
            pathFilesForPlatform = self.getPathFilesPlatform(platform)
            if j.system.fs.exists(pathFilesForPlatform):
                result.append(pathFilesForPlatform)
        return result        

    # upload the bundle
    def upload(self, remote=True, local=True):
        """
        Upload jpackages to Blobstor, default remote and local
        """
               
        self.loadActions()

        j.packages.getDomainObject(self.domain)

        updateBuildnr = False
        foundAnyPlatform = False
        #delete blob.info (not used anymore)
        if j.system.fs.exists(j.system.fs.joinPaths(self.metadataPath, "blob.info")):
            j.system.fs.remove(j.system.fs.joinPaths(self.metadataPath, "blob.info"))


        for platform in j.system.platformtype.getMyRelevantPlatforms():
            # self.getBundleKey(platform) #hash as stored in config file
            pathFilesForPlatform = self.getPathFilesPlatform(platform)

            self.log("Upload platform:'%s' files:'%s'"%(platform,pathFilesForPlatform),category="upload")

            foundAnyPlatform = True

            if not j.system.fs.exists(pathFilesForPlatform):
                path = self._getBlobInfoPath(platform)
                j.system.fs.remove(path)
                continue

            j.system.fs.removeIrrelevantFiles(pathFilesForPlatform)

            plchecksum = self.getBundleKey(platform)

            if local and remote and self.blobstorRemote <> None and self.blobstorLocal <> None:
                key, descr, uploadedAnything = self.blobstorLocal.put(pathFilesForPlatform, blobstores=[self.blobstorRemote], prevkey=plchecksum)
            elif local and self.blobstorLocal <> None:
                key, descr, uploadedAnything = self.blobstorLocal.put(pathFilesForPlatform, blobstores=[], prevkey=plchecksum)
            elif remote and self.blobstorRemote <> None:
                key, descr, uploadedAnything = self.blobstorRemote.put(pathFilesForPlatform, blobstores=[], prevkey=plchecksum)
            else:
                raise RuntimeError("need to upload to local or remote")

            if plchecksum<>key and descr<>"":
                updateBuildnr = True
                self.bundles[str(platform)] = key
                path = self._getBlobInfoPath(platform)
                j.system.fs.writeFile(path, descr)
                self.save()
                self.log("Uploaded changed bundle for platform:%s"%platform,level=5,category="upload" )
            else:
                self.log("No file change for platform:%s"%platform,level=5,category="upload" )

        actionsdir=j.system.fs.joinPaths(self.metadataPath, "actions")
        j.system.fs.removeIrrelevantFiles(actionsdir)
        taskletsChecksum, descr2 = j.tools.hash.hashDir(actionsdir)
        hrddir=j.system.fs.joinPaths(self.metadataPath, "hrdactive")
        hrdChecksum, descr2 = j.tools.hash.hashDir(hrddir)
        descrdir=j.system.fs.joinPaths(self.metadataPath, "documentation")
        descrChecksum, descr2 = j.tools.hash.hashDir(descrdir)

        if descrChecksum <> self.descrChecksum:
            self.log("Descr change, upgrade buildnr.",level=5,category="buildnr")
            #buildnr needs to go up
            updateBuildnr = True
            self.descrChecksum = descrChecksum
        else:
            self.log("Descr did not change.",level=7,category="buildnr")

        if taskletsChecksum <> self.taskletsChecksum:
            self.log("Actions change, upgrade buildnr.",level=5,category="buildnr")
            #buildnr needs to go up
            updateBuildnr = True
            self.taskletsChecksum = taskletsChecksum
        else:
            self.log("Actions did not change.",level=7,category="buildnr")            

        if hrdChecksum <> self.hrdChecksum:
            self.log("Active HRD change, upgrade buildnr.",level=5,category="buildnr")
            #buildnr needs to go up
            updateBuildnr = True
            self.hrdChecksum = hrdChecksum
        else:
            self.log("Active HRD did not change.",level=7,category="buildnr")

        if  updateBuildnr:
            self.buildNr += 1
            self.save()

        if foundAnyPlatform == False:
            self.log('No platform found for upload' )
            
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
        self.state.setIsPendingReconfiguration(True)
        j.packages._setHasPackagesPendingConfiguration(True)

    def isPendingReconfiguration(self):
        """
        Check if the JPackage needs reconfiguration
        """
        if self.state.getIsPendingReconfiguration() == 1:
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
            if j.packages._actionCheck(self, action):
                return True

            j.packages._actionSet(self, action)

        #process all dependencies
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.executeAction(action,tags,  dependencies,params=params)
        self.log('executing jpackages action ' + tags + ' ' + action)
        self.state.setCurrentAction(tags, action)
        self.actions.execute(action, tags=tags, params=params) #tags are not used today
        self.state.setCurrentActionIsDone()

#########################################################################
####################### SHOW ############################################

    def showDependencies(self):
        """
        Return all dependencies of the JPackage.
        See also: addDependency and removeDependency
        """        
        self._printList(self.getDependencies())
            
    def showDependingInstalledPackages(self):
        """
        Show which jpackages have this jpackages as dependency.
        Do this only for the installed jpackages.
        """
        self._printList(self.getDependingInstalledPackages())

    def showDependingPackages(self):
        """
        Show which jpackages have this jpackages as dependency.
        """
        self._printList(self.getDependingPackages())

    def _printList(self, arr):
        for item in arr:
            j.console.echo(item)        


#########################################################################
#######################  SUPPORTING FUNCTIONS  ##########################

    def _getDomainObject(self):
        """
        Get the domain object for this Q-Package

        @return: domain object for this Q-Package
        @rtype: Domain.Domain
        """
        return j.packages.getDomainObject(self.domain)

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
        self.supportedPlatforms=[]
        self.buildNr = 0
        self.dependencies = []


    def __cmp__(self,other):
        if other == None or other=="":
            return False
        return self.name == other.name and str(self.domain) == str(other.domain) and j.packages._getVersionAsInt(self.version) == j.packages._getVersionAsInt(other.version)

    def __repr__(self):
        return self.__str__()

    def getInteractiveObject(self):
        """
        Return the interactive version of the jpackages object
        """
        ##self.assertAccessable()
        return JPackageIObject(self)

    def _resetPreparedForUpdatingFiles(self):
        self.state.setPrepared(0)

    def __str__(self):
        return "JPackage %s %s %s" % (self.domain, self.name, self.version)

    def __eq__(self, other):
        return str(self) == str(other)

    
        
        j.packages.log(str(self) + ':' + mess, category,level=level)
        # print str(self) + ':' + mess

    def reportNumbers(self):
        #return ' metaNr:' + str(self.metaNr) + ' bundleNr:' + str(self.bundleNr) + ' buildNr:' + str(self.buildNr)
        return ' buildNr:' + str(self.buildNr)
