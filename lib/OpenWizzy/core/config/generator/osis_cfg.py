import os

from OpenWizzy import o

class OsisPyApps:

    def __init__(self, appName):
        self.appName = appName
        self.components = [('passwd', ''), ('login', self.appName),
                        ('database', self.appName),('ip', '127.0.0.1')]

    def generate_cfg(self):
        iniFile = o.system.fs.joinPaths(o.dirs.cfgDir, 'osisdb.cfg')
        if os.path.isfile(iniFile):
            ini = o.tools.inifile.open(iniFile)
        else:
            ini = o.tools.inifile.new(iniFile)

        exists = ini.checkSection(self.appName)
        if not exists:
            ini.addSection(self.appName)
            for key, value in self.components:
                ini.addParam(self.appName, key, value)
        ini.write()
