
import sys, os, inspect
from user import home

from OpenWizzy import o

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

    appDir = "/opt/openwizzy6/apps/exampleapp" ##string
    '''Application installation base folder (basedir/apps)

    @type: string
    '''
    
    baseDir = "/opt/openwizzy6" ##string
    '''openwizzy sandbox base folder

    @type: string
    '''

    cfgDir = None ##string
    '''Configuration file folder (appdir/etc)

    @type: string
    '''

    tmpDir = None ##string
    '''Temporary file folder (appdir/tmp)

    @type: string
    '''

    libDir = None ##string
    '''OpenWizzy Library folder

    @type: string
    '''

    varDir = None ##string
    '''Var folder (basedir/var)

    @type: string'''

    logDir = None ##string
    '''Log file folder (appdir/log)

    @type: string
    '''

    homeDir = None ##string
    '''Home folder

    @type: string
    '''

    pidDir = None ##string
    '''Location of the PID files, is set in the initialization of the
    application

    @type: string
    '''

    cmdbDir = None ##string
    '''CMDB storage folder (vardir/cmdb)

    @type: string
    '''

    extensionsDir = None ##string
    '''openwizzy extensions base folder (basedir/lib/openwizzy/extensions)

    @type: string
    '''

    packageDir = None
    

    binDir = None ##string
    '''Binaries folder (basedir/bin)

    @type: string
    '''

    __initialized = False ##bool

    def init(self,reinit=False):
        """Initializes all the configured directories if needed

        If a folder attribute is None, set its value to the corresponding
        default path.

        @returns: Initialization success
        @rtype: bool
        """
        self.baseDir=self.baseDir.replace("\\","/")
        if str(self.baseDir).strip()=="":
            self.baseDir="/opt/openwizzy6"
        o.system.fs.createDir(self.baseDir)
        if reinit==False and self.__initialized == True:
            return True
        if not self.appDir:
            self.appDir = os.path.join(self.baseDir,"apps")
        else:
            #localdir is appdir
            if self.appDir==".":
                self.appDir =o.system.fs.getcwd()
        if not self.varDir:
            self.varDir = os.path.join(self.baseDir,"var")
        if not self.tmpDir:
            self.tmpDir = os.path.join(self.varDir,"tmp")
        if not self.cfgDir:
            self.cfgDir = os.path.join(self.baseDir,"cfg")
        if not self.logDir:
            self.logDir = os.path.join(self.varDir,"log")
        if not self.cmdbDir:
            self.cmdbDir = os.path.join(self.varDir,"cmdb")
        if not self.packageDir:
            self.packageDir = os.path.join(self.varDir,"owpackages")
        if not self.homeDir:
            self.homeDir = pathToUnicode(os.path.join(home, ".owbase"))
        if not self.binDir:
            self.binDir = os.path.join(self.baseDir, 'bin')

        self.getLibPath()
        if o.system.platformtype.isWindows() :
            self.codeDir=os.path.join(self.baseDir, 'code')
        else:
            self.codeDir="/opt/code"

        self.hrdDir = os.path.join(self.baseDir,"cfg","hrd")
        self.configsDir = os.path.join(self.baseDir,"cfg","owconfig")

        o.system.fs.createDir(self.configsDir)
        o.system.fs.createDir(self.hrdDir)
        o.system.fs.createDir(self.tmpDir)
        o.system.fs.createDir(self.varDir)
        o.system.fs.createDir(self.logDir)
        o.system.fs.createDir(self.cmdbDir)
        o.system.fs.createDir(self.packageDir)
        o.system.fs.createDir(self.homeDir)

        # TODO: Should check for basedir also and barf if it is not set properly!
        #initialize protected dirs

        protectedDirsDir = os.path.join(self.cfgDir, 'debug', 'protecteddirs')
        if not o.system.fs.exists(protectedDirsDir):
            o.system.fs.createDir(protectedDirsDir)
        _listOfCfgFiles = o.system.fs.listFilesInDir(protectedDirsDir, filter='*.cfg')
        _protectedDirsList = []
        for _cfgFile in _listOfCfgFiles:
            _cfg = open(_cfgFile, 'r')
            _dirs = _cfg.readlines()
            for _dir in _dirs:
                _dir = _dir.replace('\n', '').strip()
                if o.system.fs.isDir(_dir):
                    _protectedDirsList.append(o.system.fs.pathNormalize(_dir))
        self.protectedDirs = _protectedDirsList

        self.deployDefaultFilesInSandbox()
        self.__initialized = True
        return True

    def getLibPath(self):
        parent = o.system.fs.getParent
        self.libDir=parent(parent(__file__))
        self.libDir=os.path.abspath(self.libDir).rstrip("/")
        return self.libDir

    def getPathOfRunningFunction(self,function):
        return inspect.getfile(function)

    def checkInProtectedDir(self,path):
        path=o.system.fs.pathNormalize(path)
        for item in self.protectedDirs :
            if path.find(item)<>-1:
                return True
        return False

    def deployDefaultFilesInSandbox(self):
        #@todo P3 let it work for windows as well
        bindest=o.system.fs.joinPaths(self.baseDir,"bin")
        utilsdest=o.system.fs.joinPaths(self.baseDir,"utils")
        cfgdest=o.system.fs.joinPaths(self.baseDir,"cfg")

        if not o.system.fs.exists(bindest) or not o.system.fs.exists(utilsdest) or not o.system.fs.exists(cfgdest):
            cfgsource=o.system.fs.joinPaths(self.libDir,"core","_defaultcontent","cfg")
            binsource=o.system.fs.joinPaths(self.libDir,"core","_defaultcontent","linux","bin")
            utilssource=o.system.fs.joinPaths(self.libDir,"core","_defaultcontent","linux","utils")
            o.system.fs.copyDirTree(binsource,bindest)
            o.system.fs.copyDirTree(utilssource,utilsdest)
            o.system.fs.copyDirTree(cfgsource,cfgdest)
            ipythondir = o.system.fs.joinPaths(os.environ['HOME'], '.ipython')
            o.system.fs.removeDirTree(ipythondir)

            
    def __str__(self):
        return str(self.__dict__) #@todo P3 implement (thisnis not working)

    __repr__=__str__
