from JumpScale import j

import JumpScale.baselib.mercurial

class JSDevelToolsInstaller:

    def __init__(self):
        self._do=j.system.installtools
        self.login=""
        self.passwd=""

    def initMercurial(self,login=None,password=None,force=False):
        if j.system.platform.ubuntu.check():
            
            config=j.clients.bitbucket._config

            path="/root/.hgrc"
            if force or not j.system.fs.exists(path) or "jumpscale" not in config.list():

                j.system.platform.ubuntu.checkInstall(["mercurial"],"hg")
                j.system.platform.ubuntu.checkInstall(["meld"],"meld")

                if login==None:
                    login=j.console.askString("JumpScale Repo Login, if unknown press enter","*")
                if password==None and login<>"*":
                    password=j.console.askPassword("JumpScale Repo Password.")
                else:
                    password="*"

                if "jumpscale" not in config.list():
                    config.add("jumpscale",{"passwd":str(password),"login":login})
                else:
                    config.configure("jumpscale",{"passwd":str(password),"login":login})
                
                hgrc="""
[ui]
username = $login
verbose=True

[extensions]
hgext.extdiff=

[extdiff]
cmd.meld=
        """
                hgrc=hgrc.replace("$login",login)

                if not j.system.fs.exists(path):
                    j.system.fs.writeFile(path,hgrc)


    def getCredentialsJumpScaleRepo(self):
        config=j.clients.bitbucket._config
        self.initMercurial()

        config=config.getConfig("jumpscale")
        self.login=config["login"]
        self.passwd=config["passwd"]


    def setCredentialsJumpScaleRepo(self):
        self.initMercurial(force=True)

    def _checkCredentials(self):
        if self.passwd=="" or self.login=="":
            self.getCredentialsJumpScaleRepo()

    def _getRemoteJSURL(self,name):
        if self.passwd=="*" or self.login=="*":
            return "https://bitbucket.org/jumpscale/%s"%(name)
        else:
            return "https://%s:%s@bitbucket.org/jumpscale/%s"%(self.login,self.passwd,name)

    def _getJSRepo(self,name):
        self._checkCredentials()
        cl=j.clients.mercurial.getClient("%s/jumpscale/%s/"%(j.dirs.codeDir,name), remoteUrl=self._getRemoteJSURL(name))
        cl.pullupdate()

    def installSublimeTextUbuntu(self):
        p=j.packages.get("jumpscale","sublimetext","3.0")
        p.install()

    def preparePlatform(self):
        if j.system.platform.ubuntu.check(False):
            self.preparePlatformUbuntu()
        else:
            raise RuntimeError("This platform is not supported")
        

    def preparePlatformUbuntu(self,reinstall=False):
        j.system.platform.ubuntu.check()

        print "Updating metadata"
        j.system.platform.ubuntu.updatePackageMetadata()

        print "Updating jpackages metadata"
        j.packages.updateMetaData(force=True)

        print "install python package"
        p=j.packages.get("jumpscale","base","2.7")
        if reinstall:
            p.install(reinstall=True)
        else:
            p.install()

    def deployExampleCode(self,debug=True):
        """
        checkout example code repo & link examples to sandbox on /opt/jumpscale/apps/examples
        """
        p=j.packages.get("jumpscale","jumpscale_examples","1.0")
        if debug:
            p.setDebugMode()
        p.install(reinstall=True)

    def deployJumpScaleLibs(self,debug=True):
        """
        checkout the jumpscale libs repo & link to python 2.7 to make it available for the developer
        """        
        p=j.packages.get("jumpscale","libs","1.0")
        if debug:
            p.setDebugMode()
        p.install(reinstall=True)

    def linkJumpScaleLibs(self):
        self.deployJumpScaleLibs(True)

    def deployJumpScaleGridMaster(self,debug=True):
        """
        checkout the jumpscale grid repo & link to python 2.7 to make it available for the developer
        """
        p=j.packages.get("jumpscale","osis","1.0")
        if debug:
            p.setDebugMode()
        p.install(reinstall=True)

        p=j.packages.get("jumpscale","grid_master","1.0")
        if debug:
            p.setDebugMode()
        p.install(reinstall=True)

        p=j.packages.get("jumpscale","grid","1.0")
        if debug:
            p.setDebugMode()
        p.install(reinstall=True)


        p=j.packages.get("jumpscale","logger","1.0")
        if debug:
            p.setDebugMode()
        p.install(reinstall=True)


        p=j.packages.get("jumpscale","grid_portal","1.0")
        if debug:
            p.setDebugMode()
        p.install(reinstall=True)

        j.tools.startupmanager.reset()
        j.tools.startupmanager.startAll()        


    def deployJumpScalePortal(self,debug=True):
        """
        checkout the jumpscale portal repo & link to python 2.7 to make it available for the developer
        an example portal will also be installed in /opt/jumpscale/apps/exampleportal
        """
        p=j.packages.get("jumpscale","portal","1.0")
        if debug:
            p.setDebugMode()
        p.install(reinstall=True)

    # def deployJumpScaleBroker(self, debug=True):
    #     p=j.packages.get("jumpscale","broker","1.0")
    #     if debug:
    #         p.setDebugMode()
    #     p.install(reinstall=True)

    def linkJumpScaleBase(self,debug=True):
        """
        checkout the jumpscale portal repo & link to python 2.7 to make it available for the developer
        an example portal will also be installed in /opt/jumpscale/apps/exampleportal
        """
        p=j.packages.findNewest("jumpscale","core")
        if debug:
            p.setDebugMode()
        p.install(reinstall=True)

    def deployDFS_IO(self):
        """
        checkout the dfs.io solution
        """
        name="dfs_io_core"     
        self._getJSRepo(name)
        dest="%s/dfs_io"%(j.dirs.libDir)
        codedir = j.system.fs.joinPaths(j.dirs.codeDir, 'jumpscale', name)
        self._do.execute("cd %s; python setup.py develop" % codedir)
        self._do.symlink("%s/jumpscale/%s/apps/dfs_io"%(j.dirs.codeDir,name),"/opt/jumpscale/apps/dfs_io")

    # def deployPuppet(self):
    #     import JumpScale.lib.puppet
    #     j.tools.puppet.install()

    def deployExamplesLibsGridPortal(self):
        """
        self.deployExampleCode()
        self.deployJumpScaleLibs()
        self.deployJumpScaleGrid()
        self.deployJumpScalePortal()
        """
        #core needs to be installed first (seperate process), then install everything else
        #self.linkJumpScaleBase()
        self.deployExampleCode()
        self.deployJumpScaleLibs()
        self.deployJumpScaleGridMaster()
        self.deployJumpScalePortal()
        # self.deployJumpScaleBroker()

