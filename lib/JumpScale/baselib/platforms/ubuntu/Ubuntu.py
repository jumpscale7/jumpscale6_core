from JumpScale import j

class Ubuntu:
    def __init__(self):
        self._aptupdated = False
        self._checked = False
        self._cache=None

    def initApt(self):
        try:
            import apt
        except ImportError:
            #we dont wont qshell to break, self.check will take of this
            return
        apt.apt_pkg.init()
        #@todo error, interface changed on ubuntu 13.10
        try:
            apt.apt_pkg.Config.set("APT::Install-Recommends", "0")
            apt.apt_pkg.Config.set("APT::Install-Suggests", "0")
        except:
            pass
        self._cache = apt.Cache()

    def check(self, die=True):
        """
        check if ubuntu or mint (which is based on ubuntu)
        """
        if not self._checked:
            try:
                import lsb_release
                info = lsb_release.get_distro_information()['ID']
                if info != 'Ubuntu' and info !='LinuxMint':
                    raise RuntimeError("Only ubuntu or mint supported.")
                self._checked = True
            except ImportError:
                self._checked = False
                if die:
                    raise RuntimeError("Only ubuntu or mint supported.")
        return self._checked

    def getVersion(self):
        """
        returns codename,descr,id,release
        known ids" raring, linuxmint
        """
        self.check()
        import lsb_release
        result=lsb_release.get_distro_information()        
        return result["CODENAME"].lower().strip(),result["DESCRIPTION"],result["ID"].lower().strip(),result["RELEASE"],

    def createUser(self,name,passwd,home=None,creategroup=True):
        import JumpScale.lib.cuisine
        c=j.tools.cuisine.api

        if home==None:
            homeexists=True
        else:
            homeexists=j.system.fs.exists(home)

        c.user_ensure(name, passwd=passwd, home=home, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=False)
        if creategroup:
            self.createGroup(name)
            self.addUser2Group(name,name)

        if home<>None and not homeexists:
            c.dir_ensure(home,owner=name,group=name)

    def createGroup(self,name):
        import JumpScale.lib.cuisine
        c=j.tools.cuisine.api
        c.group_ensure(name)

    def addUser2Group(self,group,user):
        import JumpScale.lib.cuisine
        c=j.tools.cuisine.api
        c.group_user_ensure(group, user)

            

    def checkInstall(self, packagenames, cmdname):
        """
        @param packagenames is name or array of names of ubuntu package to install e.g. curl
        @param cmdname is cmd to check e.g. curl
        """
        self.check()
        if j.basetype.list.check(packagenames):
            for packagename in packagenames:
                self.checkInstall(packagename,cmdname)
        else:
            packagename=packagenames
            result, out = j.system.process.execute("which %s" % cmdname, False)
            if result != 0:
                self.install(packagename)
            else:
                return
            result, out = j.system.process.execute("which %s" % cmdname, False)
            if result != 0:
                raise RuntimeError("Could not install package %s and check for command %s." % (packagename, cmdname))

    def install(self, packagename):
        self.check()
        if self._cache==None:
            self.initApt()

        if isinstance(packagename, basestring):
            packagename = [packagename]
        for package in packagename:
            pkg = self._cache[package]
            if not pkg.is_installed:
                print "install %s" % packagename
                pkg.mark_install()
        self._cache.commit()
        self._cache.clear()

    def installVersion(self, packageName, version):
        '''
        Installs a specific version of an ubuntu package.

        @param packageName: name of the package
        @type packageName: str

        @param version: version of the package
        @type version: str
        '''

        self.check()
        if self._cache==None:
            self.initApt()

        mainPackage = self._cache[packageName]
        versionPackage = mainPackage.versions[version].package

        if not versionPackage.is_installed:
            versionPackage.mark_install()

        self._cache.commit()
        self._cache.clear()

    def installDebFile(self, path):
        self.check()
        if self._cache==None:
            self.initApt()
        import apt.debfile
        deb = apt.debfile.DebPackage(path, cache=self._cache)
        deb.install()

    def remove(self, packagename):
        self.check()
        if self._cache==None:
            self.initApt()        
        pkg = self._cache[packagename]
        if pkg.is_installed:
            pkg.mark_delete()
        self._cache.commit()
        self._cache.clear()

    def startService(self, servicename):
        self._service(servicename, 'start')

    def stopService(self, servicename):
        self._service(servicename, 'stop')

    def disableStartAtBoot(self, servicename):
        j.system.process.execute("update-rc.d -f %s remove" % servicename)

    def _service(self, servicename, action):
        return j.system.process.execute("service %s %s" % (servicename, action))

    def updatePackageMetadata(self, force=True):
        self.check()
        if self._cache==None:
            self.initApt()        
        self._cache.update()

    def upgradePackages(self, force=True):
        self.check()
        if self._cache==None:
            self.initApt()        
        self.updatePackageMetadata()
        self._cache.upgrade()

    def listSources(self):
        from aptsources import sourceslist
        return sourceslist.SourcesList()

    def changeSourceUri(self, newuri):
        src = self.listSources()
        for entry in src.list:
            entry.uri = newuri
        src.save()
