
from JumpScale import j
from JumpScale.baselib.inifile.IniFile import IniFile

class JConfig():
    """
    jumpscale singleton class available under j.config
    Meant for non interactive access to configuration items
    """
    def getInifile(self, configtype):
        fileAlreadyExists = j.system.fs.exists(self._buildPath(configtype))
        return IniFile(self._buildPath(configtype), create=(not fileAlreadyExists))
    
    def getConfig(self, configtype):
        """
        Return dict of dicts for this configuration.
        E.g. { 'jumpscale.org'    : {url:'http://jumpscale.org', login='test'} ,
               'trac.qlayer.com' : {url:'http://trac.qlayer.com', login='mylogin'} }
        """
        ini = self.getInifile(configtype)
        return ini.getFileAsDict()
    
    def remove(self, configtype):
        j.system.fs.remove(self._buildPath(configtype))
        
    def list(self):
        """
        List all configuration types available.
        """
        jconfigPath = j.system.fs.joinPaths(j.dirs.cfgDir, "jsconfig")
        if not j.system.fs.exists(j.dirs.configsDir):
            return []
        fullpaths = j.system.fs.listFilesInDir(j.dirs.configsDir)
        return [j.system.fs.getBaseName(path)[:-4] for path in fullpaths if path.endswith(".cfg")]

    def _buildPath(self, configtype):
        return j.system.fs.joinPaths(j.dirs.configsDir, configtype + ".cfg")
