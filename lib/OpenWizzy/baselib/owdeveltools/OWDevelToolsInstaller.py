from OpenWizzy import o

import OpenWizzy.baselib.mercurial

class OWDevelToolsInstaller:

    def __init__(self):
        self._do=o.system.installtools
        o.system.platform.ubuntu.check()
        self.login=""
        self.passwd=""
        self.login="openwizzy"
        self.passwd="Kds007"


    def getCredentialsOpenWizzyRepo(self):
        login=raw_input("Pylabs Repo Login, if unknown press enter:")
        if self.login=="":
            self.login="yourname"
            
        passwd=raw_input("Pylabs Repo Passwd, if unknown press enter:")
        if self.passwd=="":
            self.passwd="passwd"

    def _checkCredentials(self):
        if self.passwd=="" or self.login=="":
            self.getCredentialsOpenWizzyRepo()

    def _getRemoteOWURL(self,name):
        return "https://%s:%s@bitbucket.org/openwizzy/%s"%(self.login,self.passwd,name)

    def _getOWRepo(self,name):
        self._checkCredentials()
        cl=o.clients.mercurial.getClient("%s/openwizzy/%s/"%(o.dirs.codeDir,name), remoteUrl=self._getRemoteOWURL(name))
        cl.pullupdate()

    def deployExampleCode(self):
        """
        checkout example code repo & link examples to sandbox on /opt/openwizzy6/apps/examples
        """
        name="openwizzy6_examples"
        self._getOWRepo(name)
        self._do.symlink("%s/openwizzy/%s/prototypes"%(o.dirs.codeDir,name),"/opt/openwizzy6/apps/prototypes")

    def deployOpenWizzyLibs(self):
        """
        checkout the openwizzy libs repo & link to python 2.7 to make it available for the developer
        """        
        name="openwizzy6_lib"
        self._getOWRepo(name)
        for item in [item for item in o.system.fs.listDirsInDir("%s/openwizzy/%s"%(o.dirs.codeDir,name),dirNameOnly=True) if item[0]<>"."]:
            src="%s/openwizzy/%s/%s"%(o.dirs.codeDir,name,item)
            dest="%s/lib/%s"%(o.dirs.libDir,item)
            self._do.symlink(src,dest)

    def deployOpenWizzyGrid(self):
        """
        checkout the openwizzy grid repo & link to python 2.7 to make it available for the developer
        """
        name="openwizzy6_grid"        
        self._getOWRepo(name)
        dest="%s/grid"%(o.dirs.libDir)
        self._do.symlink("%s/openwizzy/%s/gridlib"%(o.dirs.codeDir,name),dest)
        self._do.symlink("%s/openwizzy/%s/apps/broker"%(o.dirs.codeDir,name),"/opt/openwizzy6/apps/broker")
        self._do.symlink("%s/openwizzy/%s/apps/logger"%(o.dirs.codeDir,name),"/opt/openwizzy6/apps/logger")

    def deployOpenWizzyPortal(self):
        """
        checkout the openwizzy portal repo & link to python 2.7 to make it available for the developer
        an example portal will also be installed in /opt/openwizzy6/apps/exampleportal
        """
        name="openwizzy6_portal"        
        self._getOWRepo(name)
        dest="%s/portal"%(o.dirs.libDir)
        self._do.symlink("%s/openwizzy/%s/portallib"%(o.dirs.codeDir,name),dest)
        self._do.symlink("%s/openwizzy/%s/apps/portalbase"%(o.dirs.codeDir,name),"/opt/openwizzy6/apps/portalbase")

    def deployDFS_IO(self):
        """
        checkout the dfs.io solution
        """
        name="dfs_io_core"     
        self._getOWRepo(name)
        dest="%s/dfs_io"%(o.dirs.libDir)
        self._do.symlink("%s/openwizzy/%s/ow6libs/dfs_io"%(o.dirs.codeDir,name),dest)
        self._do.symlink("%s/openwizzy/%s/apps/dfs_io"%(o.dirs.codeDir,name),"/opt/openwizzy6/apps/dfs_io")


    def deployExamplesLibsGridPortal(self):
        """
        self.deployExampleCode()
        self.deployOpenWizzyLibs()
        self.deployOpenWizzyGrid()
        self.deployOpenWizzyPortal()
        """
        self.deployExampleCode()
        self.deployOpenWizzyLibs()
        self.deployOpenWizzyGrid()
        self.deployOpenWizzyPortal()

