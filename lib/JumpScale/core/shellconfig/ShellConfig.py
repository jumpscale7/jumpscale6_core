

from JumpScale import j
from ConfigFileManager import ConfigFileManager
import os

class Group():
    pass
  

class ShellConfig():
    """
    attach configuration items to this configure object (can happen at runtime)
    """
    def __init__(self):
        self.interactive=False
        self.debug=False
        self.ipython=False
        
    def refresh(self):
        configfiles= j.system.fs.listFilesInDir(j.dirs.configsDir)
        for file in configfiles:
            if file.find(".cfg")<>-1:
                configType=os.path.basename(file.replace(".cfg",""))
                #set configfilemanager under shellconfigure 
                self.loadConfigFile(configType)
                
    def checkCreateConfigFile(self,configType):
        """
        check if config file exists, if not create and reload
        """
        path=j.system.fs.joinPaths(j.dirs.configsDir,"%s.cfg"%configType)
        if not j.system.fs.exists(path):
            j.system.fs.createEmptyFile(path)
        self.refresh()        
    
    def loadConfigFile(self,configType):
        setattr(self,configType,ConfigFileManager(configType)) 
                
                
    def getConfigFileManager(self, configType):
        self.loadConfigFile(configType)
        try:
            #@todo need check here, if moddate on disk > when we loaded
            #refresh file
            return getattr(self, configType)
        except AttributeError:
            pass

        self.refresh()

        try:
            return getattr(self, configType)
        except AttributeError:
            raise RuntimeError(
                    'Unable to find config file manager for type %s' % \
                            configType)