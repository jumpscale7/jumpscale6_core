import time
import inspect

from JumpScale import j

from JPackageStateObject import JPackageStateObject
#from JumpScale.core.sync.Sync import SyncLocal
from ActionManager import ActionManager

from CodeManagementRecipe import CodeManagementRecipe


class JPackageObject():
    """
    Data representation of a JPackage, should contain all information contained in the jpackages.cfg
    """

    def __init__(self, domain, name, version):
        """
        Initialization of the JPackage

        @param domain:  The domain that the JPackage belongs to, can be a string or the DomainObject4
        @param name:    The name of the JPackage
        @param version: The version of the JPackage
        """

        self.supportedPlatforms=[]
        self.domain=domain
        self.name=name
        self.version=version
        self.supportedPlatforms=[]
        self.tags=[]
        self.description=""


        #checks on correctness of the parameters
        if not domain:
            raise ValueError('The domain parameter cannot be empty or None')
        if not name:
            raise ValueError('The name parameter cannot be empty or None')
        if not version:
            raise ValueError('The version parameter cannot be empty or None')

        self.buildNr=-1
        self.taskletsChecksum=""    
        
        self.configchanged=False
              
        self.metadata=None

        self.dependencies=[] #key = domain_packagename
        self.dependenciesNames={}

        self.hrd=None

        self.actions=None
                
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
            self.clean()
            self.init()
            self.load()
        self.__init=True

    def init(self):

        #create defaults for new jpackages
        hrddir=j.system.fs.joinPaths(self.getPathMetadata(),"hrd")

        if True or not j.system.fs.exists(hrddir): #@todo first True statement needs to go

            extpath=inspect.getfile(self.__init__)
            extpath=j.system.fs.getDirName(extpath)
            src=j.system.fs.joinPaths(extpath,"templates")

            if self.hrd==None:
                content="jp.domain=%s\n"%self.domain
                content+="jp.name=%s\n"%self.name
                content+="jp.version=%s\n"%self.version
                self.hrd=j.core.hrd.getHRD(content=content)

            j.system.fs.copyDirTree(src,self.getPathMetadata(), overwriteFiles=False) #do never put this on true

            #for easy development, overwrite specific implementations
            # j.system.fs.copyDirTree(src+"/actions/",self.getPathMetadata()+"/actions/", overwriteFiles=True)
            #j.system.fs.copyFile(src+"/actions/process.depcheck.py",self.getPathMetadata()+"/actions/process.depcheck.py")

            self.hrd=j.core.hrd.getHRD(path=j.system.fs.joinPaths(hrddir,"main.hrd"))

            if self.hrd.get("jp.domain",checkExists=True)<>self.domain:
                self.hrd.set("jp.domain",self.domain)
            if self.hrd.get("jp.name",checkExists=True)<>self.name:
                self.hrd.set("jp.name",self.name)
            if self.hrd.get("jp.version",checkExists=True)<>self.version:                
                self.hrd.set("jp.version",self.version)    

            descr=self.hrd.get("jp.description",checkExists=True)
            if descr<>False and descr<>"":
                self.description=descr
            if descr<>self.description:                
                self.hrd.set("jp.description",self.description)                      

            self.supportedPlatforms=self.hrd.getList("jp.supportedplatforms")

            if self.supportedPlatforms==[]:
                raise RuntimeError("supported platforms cannot be empty")

            j.system.fs.createDir(j.system.fs.joinPaths(self.getPathMetadata(),"uploadhistory"))
            j.system.fs.createDir(j.system.fs.joinPaths(self.getPathMetadata(),"files"))

            for platform in self.supportedPlatforms:
                j.system.fs.createDir(self.getPathFilesPlatform(platform))

    def clean(self):
        for item in [".quarantine",".tmb"]:
        # for item in [".quarantine",".tmb",'actions/code.getRecipe']:
            path=j.system.fs.joinPaths(self.getPathMetadata(),item)
            # print "remove:%s"%path
            j.system.fs.removeDirTree(path)
        for item in [".quarantine",".tmb"]:
            path=j.system.fs.joinPaths(self.getPathFiles(),item)
            j.system.fs.removeDirTree(path)
            # print "remove:%s"%path

        # if j.system.fs.exists(self.getPathMetadata()):
        #     for item in j.system.fs.listFilesInDir(self.getPathMetadata(),filter="*.info"):
        #         j.system.fs.remove(item)

            # for item in j.system.fs.listFilesInDir(self.getPathMetadata(),recursive=True):
            #     if item.find("$(")<>-1:
            #         j.system.fs.remove(item)

        # for item in j.system.fs.listDirsInDir("%s/actions"%self.getPathMetadata(),recursive=False):
        #     j.system.fs.removeDirTree(item)            
            # action=j.system.fs.getBaseName(item)
            # action2=""
            # if action=="configure":
            #     action2="configure"                
            # if action=="monitor":
            #     action2="monitor"
            # if action=="install":
            #     action2="postinstall"
            # if action=="prepare":
            #     action2="prepare"

            # if action2=="":
            #     continue

            # def process(path,incr):
            #     content=j.system.fs.fileGetContents(path)
            #     state="start"
            #     out=""
            #     for line in content.split("\n"):
            #         if state=="body":
            #             if line.find("def")==0:
            #                 state=="done"
            #             else:
            #                 out+="%s\n"%line
            #         if state=="start" and line.find("main")<>-1:
            #             state="body"

            #     path="%s/actions/_%s%s.py"%(self.getPathMetadata(),action2,incr)
            #     j.system.fs.writeFile(path,out)

            # files=j.system.fs.listFilesInDir(item,filter="*.py")
            # if len(files)>1:
            #     #raise RuntimeError("do only support 1 file in %s"%item)
            #     for i in range(len(files)):
            #         process(files[i],i+1)
            # else:
            #     process(files[0],"")

    def load(self,hrdDir=None,position=""):                

        #create defaults for new jpackages
        hrdpath=j.system.fs.joinPaths(self.getPathMetadata(),"hrd","main.hrd")
        if not j.system.fs.exists(hrdpath):
            self.init()
        self.hrd=j.core.hrd.getHRD(hrdpath)

        self._clear()
        self.buildNr = self.hrd.getInt("jp.buildNr")
        if not self.hrd.exists("jp.process.tcpports"):
            self.hrd.set("jp.process.tcpports","")
        if not self.hrd.exists("jp.process.startuptime"):
            self.hrd.set("jp.process.startuptime","30")
        self.startupTime = self.hrd.getInt("jp.process.startuptime")
        self.tcpPorts = [int(item) for item in self.hrd.getList("jp.process.tcpports") if item<>""]

        self.export = self.hrd.getBool("jp.export")
        self.autobuild = self.hrd.getBool("jp.autobuild")
        self.taskletsChecksum = self.hrd.get("jp.taskletschecksum")
        try:
            self.descrChecksum = self.hrd.get("jp.descrchecksum")
        except:
            hrd = self.hrd.getHrd("").getHRD("jp.name")
            hrd.set("jp.descrchecksum","")
            self.descrChecksum = self.hrd.get("jp.descrchecksum")
        try:
            self.hrdChecksum = self.hrd.get("jp.hrdchecksum")
        except:
            hrd = self.hrd.getHrd("").getHRD("jp.name")
            hrd.set("jp.hrdchecksum","")
            self.hrdChecksum = self.hrd.get("jp.hrdchecksum")

        self.supportedPlatforms = self.hrd.getList("jp.supportedplatforms")

        j.packages.getDomainObject(self.domain)

        self.blobstorRemote = None
        self.blobstorLocal = None

        self.actions = None

        self._getState()

        self.debug=self.state.debugMode

    def getCodeMgmtRecipe(self):
        hrdpath=j.system.fs.joinPaths(self.getPathMetadata(),"hrd","code.hrd")
        if not j.system.fs.exists(path=hrdpath):
            self.init()
        recipepath=j.system.fs.joinPaths(self.getPathMetadata(),"coderecipe.cfg")
        if not j.system.fs.exists(path=recipepath):
            self.init()
        return CodeManagementRecipe(hrdpath,recipepath)

    def _loadActiveHrd(self):
        """
        match hrd templates with active ones, add entries where needed
        """
        hrdtemplatesPath=j.system.fs.joinPaths(self.getPathMetadata(),"hrdactive")
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
                    j.application.loadConfig() #will load that underneath

    def loadActions(self, force=False):
        # print "loadactions:%s"%self

        force=True #@todo need more checks, now for first release do always

        if self.actions <> None and not force:
            return

        self._loadActiveHrd()

        self.check()

        if j.system.fs.isDir(self.getPathActions()):
            j.system.fs.removeDirTree(self.getPathActions())
        j.system.fs.copyDirTree(j.system.fs.joinPaths(self.getPathMetadata(),"actions"),self.getPathActions())        

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

        if self.blobstorRemote ==None or   self.blobstorLocal==None:
            from IPython import embed
            print "DEBUG NOW ooooooooooooo"
            embed()

        # print "loadactionsdone:%s"%self
            
    def getDebugMode(self):
        return self.state.debugMode

    def setDebugMode(self,dependencies=False):

        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.setDebugMode(dependencies=False)

        self.state.setDebugMode()
        self.load()
        self.log("set debug mode",category="init")

    def removeDebugMode(self,dependencies=False):

        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.removeDebugMode(dependencies=False)

        self.state.setDebugMode(mode=0)
        self.log("remove debug mode",category="init")


###############################################################
############  MAIN OBJECT METHODS (DELETE, ...)  ##############
###############################################################

    def delete(self):
        """
        Delete all metadata, files of the jpackages
        """
        self._init()
        if j.application.shellconfig.interactive:
            do = j.gui.dialog.askYesNo("Are you sure you want to remove %s_%s_%s, all metadata & files will be removed" % (self.domain, self.name, self.version))
        else:
            do = True
        if do:
            path = j.packages.getDataPath(self.domain, self.name, self.version)
            j.system.fs.removeDirTree(path)
            path = j.packages.getMetadataPath(self.domain, self.name,self.version)
            j.system.fs.removeDirTree(path)
            path = j.packages.getJPActionsPath(self.domain, self.name,self.version)
            j.system.fs.removeDirTree(path)
            
            #@todo over ftp try to delete the targz file (less urgent), check with other quality levels to make sure we don't delete files we should not delete

    def save(self, new=False):
        """
        Creates a new config file and saves the most important jpackages params in it

        @param new: True if we are saving a new Q-Package, used to ensure backwards compatibility
        @type new: boolean
        """      
        self.log('saving jpackages data to ' + self.getPathMetadata(),category="save")

        if self.buildNr == "":
            self._raiseError("buildNr cannot be empty")

        self.hrd.set("jp.buildNr",self.buildNr)        
        self.hrd.set("jp.export",self.export)
        self.hrd.set("jp.autobuild",self.autobuild)
        self.hrd.set("jp.taskletschecksum",self.taskletsChecksum)
        self.hrd.set("jp.hrdchecksum",self.hrdChecksum)
        self.hrd.set("jp.descrchecksum",self.descrChecksum)
        self.hrd.set("jp.supportedplatforms",self.supportedPlatforms)

        # for idx, dependency in enumerate(self.dependencies):
        #     self._addDependencyToHRD(idx, dependency.domain, dependency.name,minversion=dependency.minversion,maxversion=dependency.maxversion)

    def _addDependencyToHRD(self, idx, domain, name, minversion, maxversion):
        hrd = self.hrd
        basekey = 'jp.dependency.%s.%%s' % idx
        def setValue(name, value):
            hrd.set(basekey % name, value)

        setValue('domain', domain)
        setValue('name', name)
        setValue('minversion', minversion)
        setValue('maxversion', maxversion)

##################################################################################################
###################################  DEPENDENCY HANDLING  #######################################
##################################################################################################


    def loadDependencies(self):
        
        if self.dependencies==[]:

            ids = {}
            for key in self.hrd.prefix('jp.dependency'):
                try:
                    ids[int(key.split('.')[2])]=1
                except Exception,e:
                    raise RuntimeError("Error in jpackage hrd:%s"%self)

            #walk over found id's
            for id in ids.keys():
                key="jp.dependency.%s.%%s"%id
                if not self.hrd.exists('minversion'):
                    self.hrd.set(key % 'minversion',"")
                if not self.hrd.exists(key % 'maxversion'):
                    self.hrd.set(key % 'maxversion',"")
                   
                name=self.hrd.get(key % 'name')
                domain=self.hrd.get(key % 'domain')
                minversion=self.hrd.get(key % 'minversion')
                maxversion=self.hrd.get(key % 'maxversion')

                deppack=j.packages.findNewest(domain,name,\
                    minversion=minversion,maxversion=maxversion) #,platform=j.system.platformtype.myplatformdeppack.loadDependencies()

                deppackKey="%s__%s"%(deppack.domain,deppack.name)
                self.dependenciesNames[deppackKey]=deppack

                #now deps of deps
                deppack.loadDependencies()
                self.dependencies.append(deppack)
                for deppack2 in reversed(deppack.dependencies):
                    if deppack2 in self.dependencies:
                        self.dependencies.remove(deppack2)
                    self.dependencies.append(deppack2)
                    deppackKey2="%s__%s"%(deppack2.domain,deppack2.name)
                    self.dependenciesNames[deppackKey2]=deppack2
            self.dependencies.reverse()

    def addDependency(self, domain, name, supportedplatforms, minversion, maxversion, dependencytype):
        dep = DependencyDef4()
        dep.name = name
        dep.domain = domain
        dep.minversion = minversion
        dep.maxversion = maxversion
        # dep.supportedPlatforms = supportedplatforms
        # dep.dependencytype = j.enumerators.DependencyType4.getByName(dependencytype)
        # self.dependencyDefs.append(dep)
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

    def getKey(self):
        return "%s|%s|%s"%(self.domain,self.name,self.version)

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
        * lastinstalledbuildnr
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
        return j.packages.getJPActionsPath(self.domain, self.name, self.version)

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

    def buildNrIncrement(self):
        buildNr=0
        for ql in self.getQualityLevels():
            path=self.getMetadataPathQualityLevel(ql)
            path= j.system.fs.joinPaths(path,"hrd","main.hrd")
            buildNr2=j.core.hrd.getHRD(path).getInt("jp.buildNr")
            if buildNr2>buildNr:
                buildNr=buildNr2
       
        buildNr+=1
        self.buildNr=buildNr
        self.save()
        return self.buildNr
            
    def getMetadataPathQualityLevel(self,ql):
        path=j.system.fs.joinPaths(j.dirs.packageDir, "metadata", self.domain)
        if not j.system.fs.isLink(path):
            raise RuntimeError("%s needs to be link"%path)
        jpackagesdir=j.system.fs.getParent(j.system.fs.readlink(path))
        path= j.system.fs.joinPaths(jpackagesdir,ql,self.name,self.version)
        if not j.system.fs.exists(path=path):         
            raise RuntimeError("Cannot find ql dir on %s"%path)
        return path

    def getQualityLevels(self):
        path=j.system.fs.joinPaths(j.dirs.packageDir, "metadata", self.domain)
        if not j.system.fs.isLink(path):
            raise RuntimeError("%s needs to be link"%path)
        jpackagesdir=j.system.fs.getParent(j.system.fs.readlink(path))
        ql=[item for item in j.system.fs.listDirsInDir(jpackagesdir,False,True) if item<>".hg"]
        return ql

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

    def getDependencies(self):
        """
        Return the dependencies for the JPackage
        """
        self.loadDependencies()
        return self.dependencies

    def _getPackageInteractive(self,platform):

        if platform == None and len(self.supportedPlatforms) == 1:
            platform = self.supportedPlatforms[0]
        
        if platform==None and j.application.shellconfig.interactive:
            platform = j.gui.dialog.askChoice("Select platform.",self.supportedPlatforms ,str(None))
        
        if platform==None:
            platform=None
        return platform

    def getBlobInfo(self,platform,ttype):
        """
        @return blobkey,[[md5,path],...]
        """
        path=j.system.fs.joinPaths(self.getPathMetadata(),"files","%s___%s.info"%(platform,ttype))
        if j.system.fs.exists(path):
            content=j.system.fs.fileGetContents(path)
            splitted=content.split("\n")
            key=splitted[0].strip()
            result=[]
            splitted=splitted[1:]
            for item in splitted:
                item=item.strip()
                if item=="":
                    continue
                result.append([item.strip() for item in item.split("|")])
            return key,result
        else:
            return None,[]

    def getBlobItemPaths(self,platform,ttype,blobitempath):
        """
        translates the item as shown in the blobinfo to the corresponding paths (jpackageFilesPath,destpathOnSystem)
        """
        platform=platform.lower().strip()
        ttype=ttype.lower().strip()
        if ttype.find("cr_")==0:
            ttype=ttype[3:]

        if ttype in ('sitepackages', 'site-packages'):
            base=j.application.config.get("python.paths.local.sitepackages")
            systemdest = j.system.fs.joinPaths(base, blobitempath)
        elif ttype=="root":
            systemdest = "/%s"%blobitempath.lstrip("/")
        elif ttype=="base":
            systemdest = j.system.fs.joinPaths(j.dirs.baseDir, blobitempath)
        elif ttype=="etc":
            base="/etc"
            systemdest = j.system.fs.joinPaths(base, blobitempath)
        elif ttype=="tmp":
            systemdest = j.system.fs.joinPaths(j.dirs.tmpDir, blobitempath)
        elif ttype=="bin":
            base=j.application.config.get("bin.local")
            systemdest = j.system.fs.joinPaths(base, blobitempath)
        else:
            base=j.application.config.applyOnContent(ttype)
            if base==ttype:
                raise RuntimeError("Could not find ttype")
            systemdest = j.system.fs.joinPaths(base, blobitempath)
        filespath=j.system.fs.joinPaths(self.getPathFiles(),platform,ttype,blobitempath)
        return (filespath,systemdest)

    def getBlobPlatformTypes(self):
        """
        @return [[platform,ttype],...]
        """
        result=[]
        path=j.system.fs.joinPaths(self.getPathMetadata(),"files")
        if not j.system.fs.exists(path=path):
            self.init()
        infofiles=[j.system.fs.getBaseName(item) for item in j.system.fs.listFilesInDir(path,False) if item.find("___")<>-1]
        for item in infofiles:
            platform,ttype=item.split("___")
            ttype=ttype.replace(".info","")
            if ttype<>"":
                result.append([platform,ttype])
        return result

    def getCodeLocationsFromRecipe(self):
        items=[]
        for item in self.getCodeMgmtRecipe().items:
            item.systemdest
            path=item.getSource()
            if j.system.fs.isFile(path):
                path=j.system.fs.getDirName(path)
            items.append(path)
            
        items.sort()
        result=[]
        previtem="willnotfindthis"
        for x in range(len(items)):                
            item=items[x]
            # print "previtem:%s now:%s"%(previtem,item)
            if not item.find(previtem)==0:
                previtem=item
                if item not in result:
                    # print "append"
                    result.append(item) 
        
        return result

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

    def isNew(self):
        # We are new when our files have not yet been committed
        # check if our jpackages.cfg file in the repo is in the ignored or added categories
        domainObject = self._getDomainObject()
        cfgPath = j.system.fs.joinPaths(self.getPathMetadata(), JPACKAGE_CFG)
        return not domainObject._isTrackingFile(cfgPath)

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

#############################################################################
#################################  ACTIONS  ################################
#############################################################################

    def start(self,dependencies=False):
        """
        Start the JPackage, run the start tasklet(s)
        """
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.start(False)
        self.loadActions()        
        self.actions.process_start()
        self.log('start')

    def stop(self,dependencies=False):
        """
        Stop the JPackage, run the stop tasklet(s)
        """
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.stop(False)
        self.loadActions()        
        self.actions.process_stop()
        self.log('stop')

    def kill(self,dependencies=False):
        """
        Stop the JPackage, run the stop tasklet(s)
        """
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.kill(False)
        self.loadActions()        
        self.actions.process_kill()
        self.log('stop')

    def monitor(self,dependencies=False,result=True):
        """
        Stop the JPackage, run the stop tasklet(s)
        """
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                result=result & dep.monitor(False,result)
        self.loadActions()        
        print "monitor for: %s"%self
        result=result&self.actions.monitor_up_local()
        return result

    def monitor_net(self,ipaddr="localhost",dependencies=False,result=True):
        """
        Stop the JPackage, run the stop tasklet(s)
        """
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                result=result & dep.monitor(False,result)
        self.loadActions()        
        result=result&self.actions.monitor_up_net(ipaddr=ipaddr)
        return result

    def restart(self,dependencies=False):
        """
        Restart the JPackage
        """        
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.restart(False)
        self.loadActions()
        self.stop()
        self.start()

    def isrunning(self,dependencies=False,ipaddr="localhost"):
        """
        Check if application installed is running for jpackages
        """
        self.monitor(dependencies=dependencies)
        # self.monitor_up_net(dependencies=dependencies,ipaddr=ipaddr)
        self.log('isrunning')

    def reinstall(self, dependencies=False, download=True):
        """
        Reinstall the JPackage by running its install tasklet, best not to use dependancies reinstall 
        """                
        self.install(dependencies=dependencies, download=download, reinstall=True)

    def prepare(self, dependencies=True, download=True):
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.install(False, download, reinstall=False)
        self.loadActions() #reload actions to make sure new hrdactive are applied

        self.actions.install_prepare()

    def copyfiles(self, dependencies=True, download=True):
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.copyfiles(dependencies=False, download=download)

        self.loadActions() #reload actions to make sure new hrdactive are applied

        if self.debug ==True:
            self._copyfiles(doCodeRecipe=False)
            self.codeLink(dependencies=False, update=False, force=True)
        else:
            self.actions.install_copy()

    def _copyfiles(self,doCodeRecipe=True):
        for platform in j.system.fs.listDirsInDir(self.getPathFiles(),dirNameOnly=True):
            pathplatform=j.system.fs.joinPaths(self.getPathFiles(),platform)
            for ttype in j.system.fs.listDirsInDir(pathplatform,dirNameOnly=True):
                # print "type:%s,%s"%(ttype,ttype.find("cr_"))
                if doCodeRecipe==False and ttype.find("cr_")==0:
                    continue #skip the coderecipe folders
                else:
                    pathttype=j.system.fs.joinPaths(pathplatform,ttype)
                    j.system.fs.removeIrrelevantFiles(pathttype)

                    if ttype in ["etc"]:
                        applyhrd=True
                    else:
                        applyhrd=False
                    if ttype == 'debs':
                        continue #TODO shoudl we install them from here?, yes

                    tmp,destination=self.getBlobItemPaths(platform,ttype,"")
                    self.log("copy files from:%s to:%s"%(pathttype,destination))
                    self.__copyFiles(pathttype,destination,applyhrd=applyhrd)
                    

    def __copyFiles(self, path,destination,applyhrd=False):
        """
        Copy the files from package dirs (/opt/js/var/jpackages/...) to their proper location in the sandbox.

        @param destination: destination of the files
        """
        if destination=="":
            raise RuntimeError("A destination needs to be specified.") #done for safety, jpackage action scripts have to be adjusted

        print "pathplatform:%s"%path
    #    self.log("Copy files from %s to %s"%(path,destination),category="copy")
        j.system.fs.createDir(destination,skipProtectedDirs=True)
        if applyhrd:
            tmpdir=j.system.fs.getTmpDirPath()
            j.system.fs.copyDirTree(path,tmpdir)
            j.application.config.applyOnDir(tmpdir)
            j.system.fs.copyDirTree(tmpdir, destination,skipProtectedDirs=True)
            j.system.fs.removeDirTree(tmpdir)
        else:
            j.system.fs.copyDirTree(path, destination,skipProtectedDirs=True)

    def install(self, dependencies=True, download=True, reinstall=False,reinstalldeps=False):
        """
        Install the JPackage

        @param dependencies: if True, all dependencies will be installed too
        @param download:     if True, bundles of package will be downloaded too
        @param reinstall:    if True, package will be reinstalled

        when dependencies the reinstall will not be asked for there

        """        

        # If I am already installed assume my dependencies are also installed
        if self.buildNr != -1 and self.buildNr <= self.state.lastinstalledbuildnr and not reinstall:
            self.log('already installed')
            return # Nothing to do

        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.install(False, download, reinstall=reinstalldeps)
        self.loadActions() #reload actions to make sure new hrdactive are applied

        if download:
            self.download(dependencies=False)

        if reinstall or self.buildNr > self.state.lastinstalledbuildnr:
            #print 'really installing ' + str(self)
            self.log('installing')
            if self.state.checkNoCurrentAction == False:
                raise RuntimeError ("jpackages is in inconsistent state, ...")                

            self.prepare(dependencies=False)
            self.copyfiles(dependencies=False)

            self.actions.install_post()

            self.state.setLastInstalledBuildNr(self.buildNr)

        if self.buildNr==-1 or self.configchanged or reinstall or self.buildNr >= self.state.lastinstalledbuildnr:
            self.configure(dependencies=False)

        if self.debug:
            self.log('install for debug (link)')
            self.codeLink(dependencies=False, update=False, force=True)

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

    def configure(self, dependencies=False):
        """
        Configure the JPackage after installation, via the configure tasklet(s)
        """
        self.log('configure')
        self.loadActions()
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.configure(dependencies=False)

        self.actions.install_configure()
        self.actions.process_configure()
        # self.state.setIsPendingReconfiguration(False)
        j.application.loadConfig() #makes sure hrd gets reloaded to application.config object

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
                dep.codeExport(dependencies=False,update=update)
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
                dep.codeUpdate(dependencies=False,force=force)
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
                dep.codeCommit(dependencies=False,push=push)
        self.actions.code_commit()
        if push:
            self.codePush(dependencies)

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

    def codeLink(self, dependencies=False, update=False, force=False):
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
                dep.codeLink(dependencies=False, update=update,force=force)            

        self.actions.code_link(force=force)
      
    def package(self, dependencies=False,update=False):
        """
        copy files from code recipe's and also manually copied files in the files sections

        @param dependencies: whether or not to package the dependencies
        @type dependencies: boolean
        """
                
        self.loadActions()

        self.log('Package')
        # Disable action caching:
        # If a user packages for 2 different platforms in the same jshell
        # instance, the second call is just ignored, which is not desired
        # behaviour.
        # Also, when a user packages once, then sees a need to update his/her
        # code, and then packages again in the same jshell, again the second
        # time would be a non-op, which is again not desired. So we disable the
        # action caching for this action.
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.package()
        if update:
            self.actions.code_update()
        self.actions.code_package()

        newbuildNr = False

        newblobinfo = self._caculateBlobInfo()


        actionsdir=j.system.fs.joinPaths(self.getPathMetadata(), "actions")
        j.system.fs.removeIrrelevantFiles(actionsdir)
        taskletsChecksum, descr2 = j.tools.hash.hashDir(actionsdir)
        hrddir=j.system.fs.joinPaths(self.getPathMetadata(), "hrdactive")
        hrdChecksum, descr2 = j.tools.hash.hashDir(hrddir)
        descrdir=j.system.fs.joinPaths(self.getPathMetadata(), "documentation")
        descrChecksum, descr2 = j.tools.hash.hashDir(descrdir)

        if descrChecksum <> self.descrChecksum:
            self.log("Descr change.",level=5,category="buildNr")
            #buildNr needs to go up
            newbuildNr = True
            self.descrChecksum = descrChecksum
        else:
            self.log("Descr did not change.",level=7,category="buildNr")

        if taskletsChecksum <> self.taskletsChecksum:
            self.log("Actions change.",level=5,category="buildNr")
            #buildNr needs to go up
            newbuildNr = True
            self.taskletsChecksum = taskletsChecksum
        else:
            self.log("Actions did not change.",level=7,category="buildNr")            

        if hrdChecksum <> self.hrdChecksum:
            self.log("Active HRD change.",level=5,category="buildNr")
            #buildNr needs to go up
            newbuildNr = True
            self.hrdChecksum = hrdChecksum
        else:
            self.log("Active HRD did not change.",level=7,category="buildNr")

        if newbuildNr or newblobinfo:
            if newbuildNr:
                self.buildNrIncrement()
            self.log("new buildNr is:%s"%self.buildNr)
            self.save()
            self.load()

    def _caculateBlobInfo(self):
        result = False
        for platform in j.system.fs.listDirsInDir(self.getPathFiles(),dirNameOnly=True):
            pathplatform=j.system.fs.joinPaths(self.getPathFiles(),platform)
            for ttype in j.system.fs.listDirsInDir(pathplatform,dirNameOnly=True):
                pathttype=j.system.fs.joinPaths(pathplatform,ttype)
                j.system.fs.removeIrrelevantFiles(pathttype)
                md5,llist=j.tools.hash.hashDir(pathttype)
                if llist=="":
                    continue
                out="%s\n"%md5
                out+=llist

                oldkey,olditems=self.getBlobInfo(platform,ttype)
                if oldkey<>md5:
                    if not result:
                        self.buildNrIncrement()
                    result = True

                    dest=j.system.fs.joinPaths(self.getPathMetadata(),"files","%s___%s.info"%(platform,ttype))
                    j.system.fs.createDir(j.system.fs.getDirName(dest))
                    j.system.fs.writeFile(dest,out)

                    dest=j.system.fs.joinPaths(self.getPathMetadata(),"uploadhistory","%s___%s.info"%(platform,ttype))
                    out="%s | %s | %s | %s\n"%(j.base.time.getLocalTimeHR(),j.base.time.getTimeEpoch(),self.buildNr,md5)
                    j.system.fs.writeFile(dest, out, append=True)
                    self.log("Uploaded changed for platform:%s type:%s"%(platform,ttype),level=5,category="upload" )
                else:
                    self.log("No file change for platform:%s type:%s"%(platform,ttype),level=5,category="upload" )
        return result

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

    def download(self, dependencies=False, destinationDirectory=None, suppressErrors=False, allplatforms=False):
        """
        Download the jpackages & expand
        """

        if dependencies==None and j.application.shellconfig.interactive:
            dependencies = j.console.askYesNo("Do you want all depending packages to be downloaded too?")
        else:
            dependencies=dependencies
        
        self.loadActions()
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.download(dependencies=False, destinationDirectory=destinationDirectory,allplatforms=allplatforms,expand=expand)

        self.actions.install_download()

    def _download(self,destinationDirectory=None):

        j.packages.getDomainObject(self.domain)

        self.log('Downloading.')

        for platform,ttype in self.getBlobPlatformTypes():
            
            if destinationDirectory==None:
                downloadDestinationDirectory=j.system.fs.joinPaths(self.getPathFiles(),platform,ttype)
            else:
                downloadDestinationDirectory = destinationDirectory

            
            checksum,files=self.getBlobInfo(platform,ttype)

            self.log("key found:%s for platform:%s type:%s"%(checksum,platform,ttype),category="download",level=6)
            
            key="%s_%s"%(platform,ttype)

            if self.state.downloadedBlobStorKeys.has_key(key) and self.state.downloadedBlobStorKeys[key] == checksum:
                self.log("No need to download/expand for platform_type:'%s', already there."%key,level=5)
                continue

            if not self.blobstorLocal.exists(checksum):
                self.blobstorRemote.copyToOtherBlobStor(checksum, self.blobstorLocal)

            self.log("expand platform_type:%s"%key,category="download")
            j.system.fs.removeDirTree(downloadDestinationDirectory)
            j.system.fs.createDir(downloadDestinationDirectory)
            self.blobstorLocal.download(checksum, downloadDestinationDirectory)
            self.state.downloadedBlobStorKeys[key] = checksum
            self.state.save()

        return True

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

    def upload(self, remote=True, local=True,dependencies=False):
        if dependencies==None and j.application.shellconfig.interactive:
            dependencies = j.console.askYesNo("Do you want all depending packages to be downloaded too?")
        else:
            dependencies=dependencies
        
        self.loadActions()
        if dependencies:
            deps = self.getDependencies()
            for dep in deps:
                dep.upload(remote=remote, local=local,dependencies=False)

        self.actions.upload()

    def _upload(self, remote=True, local=True):
        """
        Upload jpackages to Blobstor, default remote and local
        Does always a jp.package() first
        """
        self.loadActions(force=True)
        self._caculateBlobInfo()

        for platform,ttype in self.getBlobPlatformTypes():
            key0,blobitems=self.getBlobInfo(platform,ttype)

            pathttype=j.system.fs.joinPaths(self.getPathFiles(),platform,ttype)

            if not j.system.fs.exists(pathttype):
                raise RuntimeError("Could not find files section:%s, check the files directory in your jpackages metadata dir, maybe there is a .info file which is wrong & does not exist here."%pathttype)

            self.log("Upload platform:'%s', type:'%s' files:'%s'"%(platform,ttype,pathttype),category="upload")
        
            if local and remote and self.blobstorRemote <> None and self.blobstorLocal <> None:
                key, descr, uploadedAnything = self.blobstorLocal.put(pathttype, blobstors=[self.blobstorRemote])
            elif local and self.blobstorLocal <> None:
                key, descr, uploadedAnything = self.blobstorLocal.put(pathttype, blobstors=[])
            elif remote and self.blobstorRemote <> None:
                key, descr, uploadedAnything = self.blobstorRemote.put(pathttype, blobstors=[])
            else:
                raise RuntimeError("need to upload to local or remote")

            # if uploadedAnything:
            #     self.log("Uploaded blob for %s:%s:%s to blobstor."%(self,platform,ttype))
            # else:
            #     self.log("Blob for %s:%s:%s was already on blobstor, no need to upload."%(self,platform,ttype))

            if key0<>key:
                raise RuntimeError("Corruption in upload for %s"%self)

    def waitUp(self, timeout=60,dependencies=False):        
        self.loadActions()
        if dependencies:
            deps = self.getDependencies()
        else:
            deps=[]

        start=j.base.time.getTimeEpoch()
        now=start
        while now<start+timeout:
            result=True
            for dep in deps:
                # result=result & dep.actions.monitor_up_net()
                result=result & dep.actions.monitor_up_local()
            # result=result & self.actions.monitor_up_net()
            result=result & self.actions.monitor_up_local()
            if result:
                return True
            time.sleep(0.5)
            print "waitup:%s"%self
            now=j.base.time.getTimeEpoch()
        raise RuntimeError("Timeout on waitup for jp:%s"%self)

    def waitDown(self, timeout=60,dependencies=False):        
        self.loadActions()
        if dependencies:
            deps = self.getDependencies()
        else:
            deps=[]

        start=j.base.time.getTimeEpoch()
        now=start
        while now<start+timeout:
            result=True
            for dep in deps:
                result=result and not(dep.actions.monitor_up_net()) and not(dep.actions.monitor_up_local())
            result=result and not(self.actions.monitor_up_net()) and not(self.actions.monitor_up_local())


            if result:
                return True

            time.sleep(0.5)
            print "waitdown:%s"%self
            now=j.base.time.getTimeEpoch()

        raise RuntimeError("Timeout on waitdown for jp:%s"%self)


    def processDepCheck(self, timeout=60,dependencies=False):
        #check for dependencies for process to start
        self.loadActions()
        if dependencies:
            deps = self.getDependencies()
        else:
            deps=[]            
            
        start=j.base.time.getTimeEpoch()
        now=start

        while now<start+timeout:
            result=True
            for dep in deps:
                r=dep.actions.process_depcheck()
                if r == False:
                    result = False
            r=self.actions.process_depcheck()
            if r == False:
                result = False
            if result != False:
                return True
            time.sleep(0.5)
            print "processdepcheck:%s"%self
            now=j.base.time.getTimeEpoch()
        raise RuntimeError("Timeout on check process dependencies for jp:%s"%self)



###################################################################################

    # def _iterCfgHistory(self, qualitylevel):
    #     """
    #     Iterate the history of the configuration file of this Q-Package on
    #     `qualitylevel`. For each JPackageConfig object, yield the node ID the
    #     configuration file version was committed on, and the JPackageConfig
    #     instance.

    #     Iterators are *NOT* supposed to edit the JPackageConfig file! This
    #     iterator is for read-only purposes.

    #     Also, the config file can only be used during the iteration step it is
    #     yielded!

    #     @param qualitylevel: quality level of the config file
    #     @type qualitylevel: string
    #     @return: iterator
    #     @rtype: iterator
    #     """
    #     domain = self._getDomainObject()
    #     hgc = domain.mercurialclient

    #     subPath = self._getCfgSubPath(qualitylevel)
    #     nodeIds = hgc.getFileChangeNodes(subPath)

    #     for nodeId in nodeIds:
    #         content = hgc.cat(nodeId, subPath)
    #         with contextlib.closing(StringIO(content)) as f:
    #             cfg = j.packages.pm_getJPackageConfig(f)
    #             yield nodeId, cfg

    # def _getCfgSubPath(self, qualitylevel):
    #     """
    #     Get the path of the jpackages.cfg file for this Q-Package on the argument
    #     qualitylevel. The returned path will be relative the the metadata
    #     repository root.

    #     @param qualitylevel: qualitylevel the package should be on
    #     @type qualitylevel: string
    #     @return: path of the jpackages.cfg file for `qualitylevel`
    #     @rtype: string
    #     """
    #     return j.system.fs.joinPaths(qualitylevel, self.name,
    #             self.version, JPACKAGE_CFG)

    # def codeImport(self, dependencies=False):
    #     """
    #     Import code back from system to local repo

    #     WARNING: As we cannot be sure where this code comes from, all identity
    #     information will be removed when this method is used!
    #     """
        
    #     self.loadActions()
    #     self.log("CodeImport")
    #     if dependencies:
    #         deps = self.getDependencies()
    #         for dep in deps:
    #             dep.codeImport()
    #     self.actions.code_importt()
    #     cfg = self._getConfig()
    #     cfg.clearIdentities(write=True)

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
        self.dependenciesNames = {}


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
        return ' buildNr:' + str(self.buildNr)
