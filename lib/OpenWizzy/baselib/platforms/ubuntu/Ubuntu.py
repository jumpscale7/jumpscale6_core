from OpenWizzy import o

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
        apt.apt_pkg.Config.set("APT::Install-Recommends", "0")
        apt.apt_pkg.Config.set("APT::Install-Suggests", "0")
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

    def checkInstall(self, packagenames, cmdname):
        """
        @param packagenames is name or array of names of ubuntu package to install e.g. curl
        @param cmdname is cmd to check e.g. curl
        """
        self.check()
        if o.basetype.list.check(packagenames):
            for packagename in packagenames:
                self.checkInstall(packagename,cmdname)
        else:
            packagename=packagenames
            result, out = o.system.process.execute("which %s" % cmdname, False)
            if result != 0:
                self.install(packagename)
            else:
                return
            result, out = o.system.process.execute("which %s" % cmdname, False)
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
        deb = apt.debfile.DebPackage(path)
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
        o.system.process.execute("update-rc.d -f %s remove" % servicename)

    def _service(self, servicename, action):
        return o.system.process.execute("service %s %s" % (servicename, action))

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
