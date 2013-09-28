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
        if "jumpscale" not in config.list():
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
        p=j.packages.get("jpackagesbase","sublimetext","3.0")
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

        print "install python package"
        p=j.packages.get("jpackagesbase","python","2.7")
        if reinstall:
            p.reinstall()
        else:
            p.install()

    def deployExampleCode(self):
        """
        checkout example code repo & link examples to sandbox on /opt/jumpscale/apps/examples
        """
        name="jumpscale_examples"
        self._getJSRepo(name)
        self._do.symlink("%s/jumpscale/%s/prototypes"%(j.dirs.codeDir,name),"/opt/jumpscale/apps/prototypes")
        self._do.symlink("%s/jumpscale/%s/examples"%(j.dirs.codeDir,name),"/opt/jumpscale/apps/examples")

    def deployJumpScaleLibs(self,linkonly=False):
        """
        checkout the jumpscale libs repo & link to python 2.7 to make it available for the developer
        """        
        name="jumpscale_lib"
        if (not linkonly):
            self._getJSRepo(name)
        codedir = j.system.fs.joinPaths(j.dirs.codeDir, 'jumpscale', name)
        self._do.execute("cd %s; python setup.py develop" % codedir)

    def linkJumpScaleLibs(self):
        self.deployJumpScaleLibs(True)


    def deployJumpScaleGrid(self):
        """
        checkout the jumpscale grid repo & link to python 2.7 to make it available for the developer
        """
        name="jumpscale_grid"        
        self._getJSRepo(name)
        codedir = j.system.fs.joinPaths(j.dirs.codeDir, 'jumpscale', name)
        self._do.execute("cd %s; python setup.py develop" % codedir)
        self._do.symlink("%s/apps/broker"%(codedir),"/opt/jumpscale/apps/broker")
        self._do.symlink("%s/apps/logger"%(codedir),"/opt/jumpscale/apps/logger")

        osisdir="/opt/jumpscale/apps/osis/"

        do=self._do

        if not  j.system.fs.exists(osisdir):
            do.copytreedeletefirst("%s/jumpscale/%s/apps/osis"%(j.dirs.codeDir,name),osisdir)

        for item in [item for item in j.system.fs.listDirsInDir("/opt/code/jumpscale/jumpscale_grid/apps/osis/logic",dirNameOnly=True) if item[0]<>"."]:
            src="/opt/code/jumpscale/jumpscale_grid/apps/osis/logic/%s"%(item)
            dest="%s/logic/%s"%(osisdir,item)
            self._do.symlink(src,dest)

        src="/opt/code/jumpscale/jumpscale_grid/apps/osis/_templates/"
        dest="%s/_templates"%(osisdir)
        self._do.symlink(src,dest)

        if not j.system.fs.exists(path="/etc/init.d/elasticsearch"):
            print "download / install elasticsearch"
            self._do.download("https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.3.deb","/tmp/elasticsearch.deb")
            self._do.execute("cd /tmp; dpkg -E -i elasticsearch.deb")

    def deployJumpScalePortal(self):
        """
        checkout the jumpscale portal repo & link to python 2.7 to make it available for the developer
        an example portal will also be installed in /opt/jumpscale/apps/exampleportal
        """
        name="jumpscale_portal"
        j.system.platform.ubuntu.install("redis-server")
        j.system.platform.ubuntu.install("curlftpfs")
        self._getJSRepo(name)
        codedir = j.system.fs.joinPaths(j.dirs.codeDir, 'jumpscale', name)
        self._do.execute("cd %s; python setup.py develop" % codedir)
        self._do.symlink("%s/apps/portalbase"%(codedir),"/opt/jumpscale/apps/portalbase")
        self._do.symlink("%s/apps/portalftpgateway"%(codedir),"/opt/jumpscale/apps/portalftpgateway")


        portaldir="/opt/jumpscale/apps/exampleportal/"

        if not  j.system.fs.exists(portaldir):
            src="/opt/code/jumpscale/jumpscale_examples/examples/exampleportal"
            self._do.copytreedeletefirst(src,portaldir)        

        self._do.execute("pip install pyelasticsearch mimeparse beaker")

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

    def deployPuppet(self):
        import JumpScale.lib.puppet
        j.tools.puppet.install()


    def deployExamplesLibsGridPortal(self):
        """
        self.deployExampleCode()
        self.deployJumpScaleLibs()
        self.deployJumpScaleGrid()
        self.deployJumpScalePortal()
        """
        self.deployExampleCode()
        self.deployJumpScaleLibs()
        self.deployJumpScaleGrid()
        self.deployJumpScalePortal()

    def initJumpscaleUser(self,passwd):
        home="/home/jumpscale"
        name="jumpscale"
        import JumpScale.lib.remote.cuisine
        
        homeexists=j.system.fs.exists(home)

        j.system.platform.ubuntu.createUser(name,passwd,home=home)
        c=j.remote.cuisine.api       

        if not homeexists:
            c.dir_ensure(home,owner=name,group=name,mode=770,recursive=True)

        if j.system.fs.exists("/root/.hgrc"):
            C=j.system.fs.fileGetContents("/root/.hgrc")
            C2=""

            for line in C.split("\n"):
                if line.find("[trusted]")<>-1:
                    break
                C2+="%s\n"%line

            C2+="[trusted]\n"
            C2+="users = jumpscale\n\n"

            j.system.fs.writeFile("/root/.hgrc",C2)
        

    def deployFTPServer4jpackages(self,passwd,jumpscalepasswd):
        # import JumpScale.lib.psutil
        self.initJumpscaleUser(jumpscalepasswd)

        j.system.platform.ubuntu.install("proftpd-basic")

        ftphome="/opt/jpackagesftp"
        ftpname="jpackages"

        j.system.fs.createDir("/opt/jpackagesftp")

        j.system.platform.ubuntu.createUser(ftpname,passwd,home="/home/%s"%ftpname)
        j.system.platform.ubuntu.createUser("ftp","1234")#j.base.idgenerator.generateGUID(),home="/home/ftp")
        j.system.platform.ubuntu.createGroup("proftpd")
        j.system.platform.ubuntu.addUser2Group("proftpd","proftpd")

        C="""

ServerName          "ProFTPD Default Installation"
ServerType          standalone
DefaultServer       on
Port                21
Umask               022
MaxInstances        30

RequireValidShell   no

User                proftpd
Group               proftpd

#DefaultRoot /opt/jpackagesftp

#TransferLog /var/log/proftpd/xferlog
SystemLog   /var/log/proftpd/proftpd.log

DefaultRoot                    ~

<Anonymous ~ftp>
    User ftp
    Group j.

    UserAlias anonymous ftp

    DirFakeMode 0440

    <Limit WRITE STOR MKD RMD DELE RNTO>
      DenyAll
    </Limit>

</Anonymous>

<Directory />
  AllowOverwrite  on

    <Limit WRITE STOR MKD RMD DELE RNTO>
        DenyUser ftp
    </Limit>

</Directory>


"""
        j.system.fs.writeFile("/etc/proftpd/proftpd.conf", C)

        import JumpScale.lib.remote.cuisine

        c=j.remote.cuisine.api
        c.dir_ensure(ftphome,owner=ftpname,group=ftpname,mode=770,recursive=True)

        j.system.platform.ubuntu.addUser2Group(ftpname,"jumpscale")
        j.system.platform.ubuntu.addUser2Group(ftpname,"ftp")
        j.system.platform.ubuntu.addUser2Group(ftpname,"proftpd")
        j.system.platform.ubuntu.addUser2Group("jumpscale","proftpd")
        j.system.platform.ubuntu.addUser2Group("jumpscale","ftp")

        self._do.execute("/etc/init.d/proftpd restart")

        self._do.createdir("/opt/code")
        self._do.createdir("/opt/jumpscale")

        def symlink(src,dest):
            try:
                j.system.fs.remove(dest)
            except Exception,e:
                if str(e).find("could not be removed")<>-1:
                    cmd="umount %s"%dest
                    try:
                        self._do.execute(cmd)
                    except:
                        pass
                
            j.system.fs.createDir(dest)
            cmd="mount --bind %s %s"%(src,dest)
            self._do.execute(cmd)


        symlink("/opt/code","/home/jumpscale/code")
        symlink("/opt/jumpscale","/home/jumpscale/jumpscale")
        symlink("/opt/jpackagesftp","/home/jumpscale/jpackages")
        symlink("/opt/jpackagesftp","/home/ftp/jpackages")
        symlink("/opt/jpackagesftp","/home/jpackages/jpackages")


    # def link2code(self):

    #     self._do.createdir("%s/%s"%(j.dirs.baseDir,"apps"))


