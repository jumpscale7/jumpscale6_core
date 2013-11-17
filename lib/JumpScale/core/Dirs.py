
import sys, os, inspect

from JumpScale import j


home = os.curdir                        # Default
if 'HOME' in os.environ:
    home = os.environ['HOME']
elif os.name == 'posix':
    home = os.path.expanduser("~/")
elif os.name == 'nt':                   # Contributed by Jeff Bauer
    if 'HOMEPATH' in os.environ:
        if 'HOMEDRIVE' in os.environ:
            home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
        else:
            home = os.environ['HOMEPATH']

def pathToUnicode(path):
    """
    Convert path to unicode. Use the local filesystem encoding. Will return
    path unmodified if path already is unicode.

    @param path: path to convert to unicode
    @type path: basestring
    @return: unicode path
    @rtype: unicode
    """
    if isinstance(path, unicode):
        return path

    return path.decode(sys.getfilesystemencoding())

class Dirs(object):
    """Utility class to configure and store all relevant directory paths"""

    # __initialized = False ##bool

    def __init__(self):
        '''jumpscale sandbox base folder'''
        curdir=os.path.abspath(".")

        if os.path.exists("library.zip"):
            self.frozen=True
        else:
            self.frozen=False

        iswindows=os.name=="nt"

        if iswindows or self.frozen:
            self.baseDir=curdir
        else:
            self.baseDir = "/opt/jumpscale" ##string

        self.baseDir=self.baseDir.replace("\\","/")

        '''Application installation base folder (basedir/apps)'''
        self.appDir = curdir
        
        '''Configuration file folder (appdir/etc)'''
        self.cfgDir = os.path.join(self.baseDir,"cfg")
        self._createDir(self.cfgDir)

        tpath = os.path.join(self.cfgDir,"debug")
        self._createDir(tpath)
        tpath = os.path.join(self.cfgDir,"debug","protecteddirs")
        self._createDir(tpath)
        tpath = os.path.join(self.cfgDir,"grid")
        self._createDir(tpath)
        tpath = os.path.join(self.cfgDir,"hrd")
        self._createDir(tpath)

        '''Var folder (basedir/var)'''
        if self.frozen:
            self.varDir = "/var/jumpscale"
        else:
            self.varDir = os.path.join(self.baseDir,"var")
        self._createDir(self.varDir)

        '''Temporary file folder (appdir/tmp)'''
        if iswindows or self.frozen:
            self.tmpDir = os.path.join(self.varDir,"tmp")
        else:
            self.tmpDir = "/tmp/jumpscale"
        self._createDir(self.tmpDir)

        
        if iswindows or self.frozen:
            self.libDir = os.path.join(self.baseDir,"library.zip")
        else:
            self.libDir = os.path.join(self.baseDir,"lib")
        self._createDir(self.libDir)

        if self.libDir not in sys.path:
            sys.path.insert(1,self.libDir)
        

        self.logDir = os.path.join(self.varDir,"log")
        self._createDir(self.logDir)

        self.packageDir = os.path.join(self.varDir,"jpackages")
        self._createDir(self.packageDir)

        # self.homeDir = pathToUnicode(os.path.join(home, ".jsbase"))

        self.pidDir = os.path.join(self.varDir,"log")   
        

        '''CMDB storage folder (vardir/cmdb)'''
        self.cmdbDir = os.path.join(self.varDir,"cmdb")
        self._createDir(self.cmdbDir)

        self.binDir = os.path.join(self.baseDir, 'bin')

        if self.frozen:
            self.codeDir=os.path.join(self.varDir,"code")
        else:
            self.codeDir="/opt/code"
        self._createDir(self.codeDir)

        self.hrdDir = os.path.join(self.baseDir,"cfg","hrd")
        self._createDir(self.hrdDir)

        self.configsDir = os.path.join(self.baseDir,"cfg","jsconfig")
        self._createDir(self.configsDir)


    def _createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)


    def init(self,reinit=False):
        """Initializes all the configured directories if needed

        If a folder attribute is None, set its value to the corresponding
        default path.

        @returns: Initialization success
        @rtype: bool
        """

        if reinit==False and self.__initialized == True:
            return True

        if j.system.platformtype.isWindows() :
            self.codeDir=os.path.join(self.baseDir, 'code')

        self.getLibPath()

        self.loadProtectedDirs()

        self.deployDefaultFilesInSandbox()
        self.__initialized = True
        return True


    def getLibPath(self):
        parent = j.system.fs.getParent
        self.libDir=parent(parent(__file__))
        self.libDir=os.path.abspath(self.libDir).rstrip("/")
        return self.libDir

    def getPathOfRunningFunction(self,function):
        return inspect.getfile(function)

    def loadProtectedDirs(self):
        protectedDirsDir = os.path.join(self.cfgDir, 'debug', 'protecteddirs')
        if not os.path.exists(protectedDirsDir):
            self._createDir(protectedDirsDir)
        _listOfCfgFiles = j.system.fs.listFilesInDir(protectedDirsDir, filter='*.cfg')
        _protectedDirsList = []
        for _cfgFile in _listOfCfgFiles:
            _cfg = open(_cfgFile, 'r')
            _dirs = _cfg.readlines()
            for _dir in _dirs:
                _dir = _dir.replace('\n', '').strip()
                if j.system.fs.isDir(_dir):
                    # npath=j.system.fs.pathNormalize(_dir)
                    if _dir not in _protectedDirsList:
                        _protectedDirsList.append(_dir)
        self.protectedDirs = _protectedDirsList


    def addProtectedDir(self,path,name="main"):
        if j.system.fs.isDir(path):
            path=j.system.fs.pathNormalize(path)
            configfile=os.path.join(self.cfgDir, 'debug', 'protecteddirs',"%s.cfg"%name)
            if not j.system.fs.exists(configfile):
                j.system.fs.writeFile(configfile,"")
            content=j.system.fs.fileGetContents(configfile)
            if path not in content.split("\n"):
                content+="%s\n"%path
                j.system.fs.writeFile(configfile,content)
            self.loadProtectedDirs()

    def removeProtectedDir(self,path):
        path=j.system.fs.pathNormalize(path)
        protectedDirsDir = os.path.join(self.cfgDir, 'debug', 'protecteddirs')
        _listOfCfgFiles = j.system.fs.listFilesInDir(protectedDirsDir, filter='*.cfg')
        for _cfgFile in _listOfCfgFiles:
            _cfg = open(_cfgFile, 'r')
            _dirs = _cfg.readlines()
            out=""
            found=False
            for _dir in _dirs:
                _dir = _dir.replace('\n', '').strip()
                if _dir==path:
                    #found, need to remove
                    found=True
                else:
                    out+="%s\n"%_dir
            if found:
                j.system.fs.writeFile(_cfgFile,out)
                self.loadProtectedDirs()


    def checkInProtectedDir(self,path):
        path=j.system.fs.pathNormalize(path)
        for item in self.protectedDirs :
            if path.find(item)!=-1:
                return True
        return False

    def deployDefaultFilesInSandbox(self):
        iswindows=os.name=="nt"
        if self.frozen or iswindows:
            return

        #@todo P3 let it work for windows as well
        bindest=j.system.fs.joinPaths(self.baseDir,"bin")
        utilsdest=j.system.fs.joinPaths(self.baseDir,"utils")
        cfgdest=j.system.fs.joinPaths(self.baseDir,"cfg")

        if not os.path.exists(bindest) or not os.path.exists(utilsdest) or not os.path.exists(cfgdest):
            cfgsource=j.system.fs.joinPaths(self.libDir,"core","_defaultcontent","cfg")
            binsource=j.system.fs.joinPaths(self.libDir,"core","_defaultcontent","linux","bin")
            utilssource=j.system.fs.joinPaths(self.libDir,"core","_defaultcontent","linux","utils")
            j.system.fs.copyDirTree(binsource,bindest)
            j.system.fs.copyDirTree(utilssource,utilsdest)
            j.system.fs.copyDirTree(cfgsource,cfgdest,overwriteFiles=False)
            ipythondir = j.system.fs.joinPaths(os.environ['HOME'], '.ipython')
            j.system.fs.removeDirTree(ipythondir)
            j.packages.reloadconfig()

            
    def __str__(self):
        return str(self.__dict__) #@todo P3 implement (thisnis not working)

    __repr__=__str__
