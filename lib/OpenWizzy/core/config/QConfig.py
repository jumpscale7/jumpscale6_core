
from OpenWizzy import o
from OpenWizzy.baselib.inifile.IniFile import IniFile

class QConfig():
    """
    openwizzy singleton class available under o.config
    Meant for non interactive access to configuration items
    """
    def getInifile(self, configtype):
        fileAlreadyExists = o.system.fs.exists(self._buildPath(configtype))
        return IniFile(self._buildPath(configtype), create=(not fileAlreadyExists))
    
    def getConfig(self, configtype):
        """
        Return dict of dicts for this configuration.
        E.g. { 'openwizzy.org'    : {url:'http://openwizzy.org', login='test'} ,
               'trac.qlayer.com' : {url:'http://trac.qlayer.com', login='mylogin'} }
        """
        ini = self.getInifile(configtype)
        return ini.getFileAsDict()
    
    def remove(self, configtype):
        o.system.fs.removeFile(self._buildPath(configtype))
        
    def list(self):
        """
        List all configuration types available.
        """
        qconfigPath = o.system.fs.joinPaths(o.dirs.cfgDir, "qconfig")
        if not o.system.fs.exists(qconfigPath):
            return []
        fullpaths = o.system.fs.listFilesInDir(qconfigPath)
        return [o.system.fs.getBaseName(path)[:-4] for path in fullpaths if path.endswith(".cfg")]

    def _buildPath(self, configtype):
        return o.system.fs.joinPaths(o.dirs.cfgDir, "qconfig", configtype + ".cfg")
