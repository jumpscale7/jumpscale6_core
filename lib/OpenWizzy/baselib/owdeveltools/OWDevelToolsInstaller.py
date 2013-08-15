from OpenWizzy import o

import OpenWizzy.baselib.mercurial

class OWDevelToolsInstaller:

    def __init__(self):
        self._do=o.system.installtools
        self.login=""
        self.passwd=""

    def getCredentialsOpenWizzyRepo(self):
        o.application.shellconfig.interactive=True
        self.login=o.console.askString("OpenWizzy Repo Login, if unknown press enter")
        if self.login=="":
            self.login="*"
            
        self.passwd=o.console.askPassword("OpenWizzy Repo Passwd, if unknown press enter", False)
        if self.passwd=="":
            self.passwd="*"

    def _checkCredentials(self):
        if self.passwd=="" or self.login=="":
            self.getCredentialsOpenWizzyRepo()

    def _getRemoteOWURL(self,name):
        if self.passwd=="*" or self.login=="*":
            return "https://bitbucket.org/openwizzy/%s"%(name)
        else:
            return "https://%s:%s@bitbucket.org/openwizzy/%s"%(self.login,self.passwd,name)

    def _getOWRepo(self,name):
        o.application.shellconfig.interactive=True
        self._checkCredentials()
        cl=o.clients.mercurial.getClient("%s/openwizzy/%s/"%(o.dirs.codeDir,name), remoteUrl=self._getRemoteOWURL(name))
        cl.pullupdate()

    def installSublimeTextUbuntu(self):
        do=o.develtools.installer

        do.execute("curl https://bitbucket.org/incubaid/develtools/raw/default/sublimetext/install.sh | sh")
        

    def preparePlatformUbuntu(self):
        o.system.platform.ubuntu.check()
        do=o.system.installtools

        print "Updating metadata"
        o.system.platform.ubuntu.updatePackageMetadata()

        debpackages = ('python2.7','nginx', 'curl', 'mc', 'ssh', 'mercurial', 'python-gevent', 'python-simplejson', 'python-numpy',
                        'byobu', 'python-apt','ipython','python-pip','python-imaging','python-requests',"python-paramiko","gcc",
                        "g++","python-dev","python-mhash","python-snappy","python-beaker","python-mimeparse","python-m2crypto",
                        "openjdk-7-jre")

        for name in debpackages:
            print "check install %s"%name
            o.system.platform.ubuntu.install(name)

        o.system.platform.ubuntu.remove('python-zmq')
        pypackages = ('urllib3', 'ujson', 'blosc', 'pylzma','circus', 'msgpack-python>=0.3.0', 'pyzmq==13.0.2')
        pypackages = [ '"%s"' % x for x in pypackages ]
        do.execute("pip install %s" % ' '.join(pypackages))

    def deployExampleCode(self):
        """
        checkout example code repo & link examples to sandbox on /opt/openwizzy6/apps/examples
        """
        name="openwizzy6_examples"
        self._getOWRepo(name)
        self._do.symlink("%s/openwizzy/%s/prototypes"%(o.dirs.codeDir,name),"/opt/openwizzy6/apps/prototypes")
        self._do.symlink("%s/openwizzy/%s/examples"%(o.dirs.codeDir,name),"/opt/openwizzy6/apps/examples")

    def deployOpenWizzyLibs(self,linkonly=False):
        """
        checkout the openwizzy libs repo & link to python 2.7 to make it available for the developer
        """        
        name="openwizzy6_lib"
        if not linkonly:
            self._getOWRepo(name)
        for item in [item for item in o.system.fs.listDirsInDir("%s/openwizzy/%s"%(o.dirs.codeDir,name),dirNameOnly=True) if item[0]<>"."]:
            src="%s/openwizzy/%s/%s"%(o.dirs.codeDir,name,item)
            dest="%s/lib/%s"%(o.dirs.libDir,item)
            self._do.symlink(src,dest)
        dest="%s/lib/__init__.py"%(o.dirs.libDir)
        o.system.fs.writeFile(dest,"")

    def linkOpenWizzyLibs(self):
        self.deployOpenWizzyLibs(True)


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

        osisdir="/opt/openwizzy6/apps/osis/"

        do=self._do

        if not  o.system.fs.exists(osisdir):
            do.copytreedeletefirst("%s/openwizzy/%s/apps/osis"%(o.dirs.codeDir,name),osisdir)

        for item in [item for item in o.system.fs.listDirsInDir("/opt/code/openwizzy/openwizzy6_grid/apps/osis/logic",dirNameOnly=True) if item[0]<>"."]:
            src="/opt/code/openwizzy/openwizzy6_grid/apps/osis/logic/%s"%(item)
            dest="%s/logic/%s"%(osisdir,item)
            self._do.symlink(src,dest)

        src="/opt/code/openwizzy/openwizzy6_grid/apps/osis/_templates/"
        dest="%s/_templates"%(osisdir)
        self._do.symlink(src,dest)

        if not o.system.fs.exists(path="/etc/init.d/elasticsearch"):
            print "download / install elasticsearch"
            self._do.download("https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.3.deb","/tmp/elasticsearch.deb")
            self._do.execute("cd /tmp; dpkg -E -i elasticsearch.deb")

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
        self._do.symlink("%s/openwizzy/%s/apps/portalftpgateway"%(o.dirs.codeDir,name),"/opt/openwizzy6/apps/portalftpgateway")

        o.system.platform.ubuntu.install("redis-server")
        o.system.platform.ubuntu.install("curlftpfs")

        portaldir="/opt/openwizzy6/apps/exampleportal/"

        if not  o.system.fs.exists(portaldir):
            src="/opt/code/openwizzy/openwizzy6_examples/examples/exampleportal"
            self._do.copytreedeletefirst(src,portaldir)        

        self._do.execute("pip install pyelasticsearch mimeparse beaker")

    def deployDFS_IO(self):
        """
        checkout the dfs.io solution
        """
        name="dfs_io_core"     
        self._getOWRepo(name)
        dest="%s/dfs_io"%(o.dirs.libDir)
        self._do.symlink("%s/openwizzy/%s/ow6libs/dfs_io"%(o.dirs.codeDir,name),dest)
        self._do.symlink("%s/openwizzy/%s/apps/dfs_io"%(o.dirs.codeDir,name),"/opt/openwizzy6/apps/dfs_io")

    def deployPuppet(self):
        import OpenWizzy.lib.puppet
        o.tools.puppet.install()


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

    def initJumpCodeUser(self,passwd):
        home="/home/jumpcode"
        name="jumpcode"
        import OpenWizzy.lib.cuisine
        o.system.platform.ubuntu.createUser(name,passwd,home=home)
        c=o.tools.cuisine.api        
        c.dir_ensure(home,owner=name,group=name,recursive=True)

    def deployFTPServer4qpackages(self,passwd,jumpcodepasswd):
        # import OpenWizzy.lib.psutil
        self.initJumpCodeUser(jumpcodepasswd)

        o.system.platform.ubuntu.install("proftpd-basic")

        ftphome="/opt/opackagesftp"
        ftpname="opackages"

        o.system.platform.ubuntu.createUser(ftpname,passwd,home="/home/%s"%ftpname)
        o.system.platform.ubuntu.createUser("ftp","1234")#o.base.idgenerator.generateGUID(),home="/home/ftp")
        o.system.platform.ubuntu.createGroup("proftpd")
        o.system.platform.ubuntu.addUser2Group("proftpd","proftpd")

        C="""
ServerName          "ProFTPD Default Installation"
ServerType          standalone
DefaultServer       on
Port                2100
Umask               022
MaxInstances        30

User                proftpd
Group               proftpd

#DefaultRoot /opt/qpackagesftp

#TransferLog /var/log/proftpd/xferlog
SystemLog   /var/log/proftpd/proftpd.log

DefaultRoot                    ~

<Directory />
  AllowOverwrite        on
</Directory>

<Anonymous ~ftp>
    User ftp
    Group opackages

    UserAlias anonymous ftp

    DirFakeMode 0444
</Anonymous>

"""
        o.system.fs.writeFile("/etc/proftpd/proftpd.conf", C)

        import OpenWizzy.lib.cuisine

        c=o.tools.cuisine.api
        c.dir_ensure(ftphome,owner=ftpname,group=ftpname,recursive=True)

        o.system.platform.ubuntu.addUser2Group(ftpname,"jumpcode")
        o.system.platform.ubuntu.addUser2Group("jumpcode","proftpd")
        o.system.platform.ubuntu.addUser2Group("jumpcode","ftp")

        self._do.execute("/etc/init.d/proftpd restart")

        def symlink(src,dest):
            o.system.fs.remove(dest)
            cmd="mount --bind %s %s"%(src,dest)
            self._do.execute(cmd)


        symlink("/opt/code","/home/jumpcode/code")
        symlink("/opt/openwizzy6","/home/jumpcode/openwizzy")
        symlink("/opt/opackagesftp","/home/jumpcode/opackages")
        symlink("/opt/opackagesftp","/home/ftp/opackages")
        symlink("/opt/opackagesftp","/home/opackages/opackages")


    def link2code(self):

        pythpath="/usr/lib/python2.7/"
        if not o.system.fs.exists(pythpath):
            raise RuntimeError("Could not find python 2.7 env on %s"%pythpath)

        owdir="%s/OpenWizzy"%pythpath
        self._do.createdir(owdir)

        libDir="/opt/code/openwizzy/openwizzy6_core/lib/OpenWizzy"

        self._do.copydeletefirst("%s/__init__.py"%libDir,"%s/__init__.py"%owdir)
        srcdir=libDir
        for item in ["base","baselib","core"]:
            self._do.symlink("%s/%s"%(srcdir,item),"%s/%s"%(owdir,item))  

        self._do.createdir("%s/%s"%(o.dirs.baseDir,"apps"))

        src="%s/../../shellcmds"%libDir
        dest="%s/shellcmds"%o.dirs.baseDir
        self._do.symlink(src,dest)

        for item in o.system.fs.listFilesInDir(dest,filter="*.py"):
            C="python %s/%s $@"%(dest,o.system.fs.getBaseName(item))
            path="/usr/bin/%s"%o.system.fs.getBaseName(item).replace(".py","")
            o.system.fs.writeFile(path,C)
            cmd='chmod 777 %s'%path
            o.system.process.execute(cmd)


