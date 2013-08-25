from JumpScale import j

import JumpScale.baselib.mercurial

class OWDevelToolsInstaller:

    def __init__(self):
        self._do=j.system.installtools
        self.login=""
        self.passwd=""

    def getCredentialsJumpScaleRepo(self):
        j.application.shellconfig.interactive=True
        self.login=j.console.askString("JumpScale Repo Login, if unknown press enter")
        if self.login=="":
            self.login="*"
            
        self.passwd=j.console.askPassword("JumpScale Repo Passwd, if unknown press enter", False)
        if self.passwd=="":
            self.passwd="*"

    def _checkCredentials(self):
        if self.passwd=="" or self.login=="":
            self.getCredentialsJumpScaleRepo()

    def _getRemoteOWURL(self,name):
        if self.passwd=="*" or self.login=="*":
            return "https://bitbucket.org/jumpscale/%s"%(name)
        else:
            return "https://%s:%s@bitbucket.org/jumpscale/%s"%(self.login,self.passwd,name)

    def _getOWRepo(self,name):
        j.application.shellconfig.interactive=True
        self._checkCredentials()
        cl=j.clients.mercurial.getClient("%s/jumpscale/%s/"%(j.dirs.codeDir,name), remoteUrl=self._getRemoteOWURL(name))
        cl.pullupdate()

    def installSublimeTextUbuntu(self):
        do=j.develtools.installer

        do.execute("curl https://bitbucket.org/incubaid/develtools/raw/default/sublimetext/install.sh | sh")
        

    def preparePlatformUbuntu(self):
        j.system.platform.ubuntu.check()
        do=j.system.installtools

        print "Updating metadata"
        j.system.platform.ubuntu.updatePackageMetadata()

        debpackages = ('python2.7','nginx', 'curl', 'mc', 'ssh', 'mercurial', 'python-gevent', 'python-simplejson', 'python-numpy',
                        'byobu', 'python-apt','ipython','python-pip','python-imaging','python-requests',"python-paramiko","gcc",
                        "g++","python-dev","python-mhash","python-snappy","python-beaker","python-mimeparse","python-m2crypto",
                        "openjdk-7-jre")

        for name in debpackages:
            print "check install %s"%name
            j.system.platform.ubuntu.install(name)

        j.system.platform.ubuntu.remove('python-zmq')
        pypackages = ('urllib3', 'ujson', 'blosc', 'pylzma','circus', 'msgpack-python>=0.3.0', 'pyzmq==13.0.2')
        pypackages = [ '"%s"' % x for x in pypackages ]
        do.execute("pip install %s" % ' '.join(pypackages))

    def deployExampleCode(self):
        """
        checkout example code repo & link examples to sandbox on /opt/jumpscale/apps/examples
        """
        name="jumpscale_examples"
        self._getOWRepo(name)
        self._do.symlink("%s/jumpscale/%s/prototypes"%(j.dirs.codeDir,name),"/opt/jumpscale/apps/prototypes")
        self._do.symlink("%s/jumpscale/%s/examples"%(j.dirs.codeDir,name),"/opt/jumpscale/apps/examples")

    def deployJumpScaleLibs(self,linkonly=False):
        """
        checkout the jumpscale libs repo & link to python 2.7 to make it available for the developer
        """        
        name="jumpscale_lib"
        if not linkonly:
            self._getOWRepo(name)
        jumpscalelib = "%s/jumpscale/%s"%(j.dirs.codeDir,name)
        if not j.system.fs.exists(jumpscalelib):
            return
        for item in [item for item in j.system.fs.listDirsInDir(jumpscalelib,dirNameOnly=True) if item[0]<>"."]:
            src="%s/jumpscale/%s/%s"%(j.dirs.codeDir,name,item)
            dest="%s/lib/%s"%(j.dirs.libDir,item)
            self._do.symlink(src,dest)
        dest="%s/lib/__init__.py"%(j.dirs.libDir)
        j.system.fs.writeFile(dest,"")

    def linkJumpScaleLibs(self):
        self.deployJumpScaleLibs(True)


    def deployJumpScaleGrid(self):
        """
        checkout the jumpscale grid repo & link to python 2.7 to make it available for the developer
        """
        name="jumpscale_grid"        
        self._getOWRepo(name)
        dest="%s/grid"%(j.dirs.libDir)
        self._do.symlink("%s/jumpscale/%s/gridlib"%(j.dirs.codeDir,name),dest)
        self._do.symlink("%s/jumpscale/%s/apps/broker"%(j.dirs.codeDir,name),"/opt/jumpscale/apps/broker")
        self._do.symlink("%s/jumpscale/%s/apps/logger"%(j.dirs.codeDir,name),"/opt/jumpscale/apps/logger")

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
        self._getOWRepo(name)
        dest="%s/portal"%(j.dirs.libDir)
        self._do.symlink("%s/jumpscale/%s/portallib"%(j.dirs.codeDir,name),dest)
        self._do.symlink("%s/jumpscale/%s/apps/portalbase"%(j.dirs.codeDir,name),"/opt/jumpscale/apps/portalbase")
        self._do.symlink("%s/jumpscale/%s/apps/portalftpgateway"%(j.dirs.codeDir,name),"/opt/jumpscale/apps/portalftpgateway")

        j.system.platform.ubuntu.install("redis-server")
        j.system.platform.ubuntu.install("curlftpfs")

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
        self._getOWRepo(name)
        dest="%s/dfs_io"%(j.dirs.libDir)
        self._do.symlink("%s/jumpscale/%s/ow6libs/dfs_io"%(j.dirs.codeDir,name),dest)
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
        import JumpScale.lib.cuisine
        
        homeexists=j.system.fs.exists(home)

        j.system.platform.ubuntu.createUser(name,passwd,home=home)
        c=j.tools.cuisine.api       

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
        

    def deployFTPServer4qpackages(self,passwd,jumpscalepasswd):
        # import JumpScale.lib.psutil
        self.initJumpscaleUser(jumpscalepasswd)

        j.system.platform.ubuntu.install("proftpd-basic")

        ftphome="/opt/jspackagesftp"
        ftpname="jspackages"

        j.system.fs.createDir("/opt/jspackagesftp")

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

#DefaultRoot /opt/qpackagesftp

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

        import JumpScale.lib.cuisine

        c=j.tools.cuisine.api
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
        symlink("/opt/jspackagesftp","/home/jumpscale/jspackages")
        symlink("/opt/jspackagesftp","/home/ftp/jspackages")
        symlink("/opt/jspackagesftp","/home/jspackages/jspackages")


    def link2code(self):

        pythpath="/usr/lib/python2.7/"
        if not j.system.fs.exists(pythpath):
            raise RuntimeError("Could not find python 2.7 env on %s"%pythpath)

        owdir="%s/JumpScale"%pythpath
        self._do.createdir(owdir)

        libDir="/opt/code/jumpscale/jumpscale_core/lib/JumpScale"

        self._do.copydeletefirst("%s/__init__.py"%libDir,"%s/__init__.py"%owdir)
        srcdir=libDir
        for item in ["base","baselib","core"]:
            self._do.symlink("%s/%s"%(srcdir,item),"%s/%s"%(owdir,item))  

        self._do.createdir("%s/%s"%(j.dirs.baseDir,"apps"))

        src="%s/../../shellcmds"%libDir
        dest="%s/shellcmds"%j.dirs.baseDir
        self._do.symlink(src,dest)

        for item in j.system.fs.listFilesInDir(dest,filter="*.py"):
            C="python %s/%s $@"%(dest,j.system.fs.getBaseName(item))
            path="/usr/bin/%s"%j.system.fs.getBaseName(item).replace(".py","")
            j.system.fs.writeFile(path,C)
            cmd='chmod 777 %s'%path
            j.system.process.execute(cmd)

        self.linkJumpScaleLibs()


