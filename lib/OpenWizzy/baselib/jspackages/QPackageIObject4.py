from OpenWizzy import o

class QPackageIObject4:
    
    def __init__(self, owpackage):
        self.owpackage = owpackage
        self.setDebugMode = owpackage.setDebugMode
        self.getDebugMode = owpackage.getDebugMode
        self.removeDebugMode = owpackage.removeDebugMode
        self.prepareForUpdatingFiles = owpackage.prepareForUpdatingFiles
        self.getBrokenDependencies = owpackage.getBrokenDependencies
        self.getDependencyTree = owpackage.getDependencyTree
        self.getBuildDependencyTree = owpackage.getBuildDependencyTree
        self.getRuntimeDependencyTree = owpackage.getRuntimeDependencyTree
        self.install = owpackage.install
        self.reload = owpackage.load
        self.delete = owpackage.delete
        self.upload = owpackage.upload
        self.codeCommit = owpackage.codeCommit
        self.codeExport = owpackage.codeExport
        self.codeImport = owpackage.codeImport
        self.codeLink = owpackage.codeLink
        self.codePush = owpackage.codePush
        self.codeUpdate = owpackage.codeUpdate

    #def quickPackage(self):
        #"""
        #The following process will be followed
        #- checkout code -> sandbox
        #- build code (if needed)
        #- package code -> owpackage files directory
        #when ready to quickPackage your owpackages you will still have to do a i.qp.publishAll()
        #"""
        #self.owpackage.prepareForUpdatingFiles(False)
        #self.owpackage.checkout()
        #self.owpackage.compile()
        #self.owpackage.package()
        ##i.qp.publishDomain(self.package.domain)
        
    def _printList(self, arr):
        for item in arr:
            o.console.echo(item)        
    
    def showDependencies(self):
        """
        Return all dependencies of the QPackage.
        See also: addDependency and removeDependency
        """
        
        platform = o.console.askChoice(o.enumerators.PlatformType.ALL, "Please select a platform")
        recursive = o.console.askYesNo("Recursive?")
        self._printList(self.owpackage.getDependencies(platform, recursive))
        
    def showBuildDependencies(self):
        """
        Return the build dependencies of the QPackage.
        See also: addDependency and removeDependency
        """
        
        ##self.assertAccessable()
        platform = o.console.askChoice(o.enumerators.PlatformType.ALL, "Please select a platform")
        recursive = o.console.askYesNo("Recursive?")
        self._printList(self.owpackage.getBuildDependencies(platform, recursive))
        
    def showRuntimeDependencies(self):
        """
        Return the runtime dependencies of the QPackage.
        See also: addDependency and removeDependency
        """
        
        ##self.assertAccessable()
        platform = o.console.askChoice(o.enumerators.PlatformType.ALL, "Please select a platform")
        recursive = o.console.askYesNo("Recursive?")
        self._printList(self.owpackage.getRuntimeDependencies(platform, recursive))
    
    def showDependingInstalledPackages(self):
        """
        Show which owpackages have this owpackage as dependency.
        Do this only for the installed owpackages.
        """
        
        ##self.assertAccessable()
        recursive = o.console.askYesNo("Recursive?")
        self._printList(self.owpackage.getDependingInstalledPackages(recursive))

    def showDependingPackages(self):
        """
        Show which owpackages have this owpackage as dependency.
        """

        ##self.assertAccessable()
        platform = o.console.askChoice(o.enumerators.PlatformType.ALL, "Please select a platform")
        recursive = o.console.askYesNo("Recursive?")
        self._printList(self.owpackage.getDependingPackages(recursive, platform))

    def backup(self):
        """
        Make a backup for this package by running its backup tasklet.
        """
        
        ##self.assertAccessable()
        url = o.console.askString("Url to backup to?")
        self.owpackage.backup(url)
        
    def restore(self):
        """
        Restore a owpackage from specified url by running its restore tasklet.
        """
        
        url = o.console.askString("Url to restore from?")
        self.owpackage.restore(url)


    def packageupload(self, platform=False):
        self.package(platform)
        self.upload()
        
        
    def configure(self):
        """
        Configure this owpackage by running its checkout tasklet.
        """
        
        ##self.assertAccessable()
        #dependencies = o.console.askYesNo("Do you want the dependencies to be configured too?")
        self.owpackage.configure()

    def start(self):
        """
        Start the QPackage by running the start tasklet.
        """
        
        self.owpackage.start()


    def stop(self):
        """
        Stop the QPackage by running the stop tasklet.
        """

        self.owpackage.stop()


    def package(self, platform=False):
        """
        Package this QPackage by running its package tasklet.
        """
        
        if platform == False and len(self.owpackage.supportedPlatforms) == 1:
            platform = self.owpackage.supportedPlatforms[0]
        
        while not platform: 
            platform = o.gui.dialog.askChoice("Select platform. If multiple platforms please quit, is not supported.", o.enumerators.PlatformType.ALL)    
        self.owpackage.package(platform=platform)
     
          
    def reinstall(self, dependencies=False, download=True):
        """
        Reinstall the QPackage by running its install tasklet, best not to use dependancies reinstall 
        """        
        self.owpackage.install(dependencies=dependencies, download=download, reinstall=True)
          
        
    def download(self):
        """
        Download the bundle of this package from the bundle server through ftp as specified in the bundledownload property of the domain of this package.
        This is the invers operation from upload.
        """
        
        ##self.assertAccessable()
        dependencies = o.console.askYesNo("Do you want the bundles of all depending packages to be downloaded too?")
        self.owpackage.download(dependencies)


    def getDescription(self):
        """
        Return the description of this package.
        """

        ##self.assertAccessable()
        return self.owpackage.description

    def __str__(self):
        #if not self.owpackage.assertAccessable():
        return "IPackage %s %s %s" % (self.owpackage.domain, self.owpackage.name, self.owpackage.version)
        #else:
        #    return "Deleted IPackage %s %s %s" % (self.owpackage.domain,self.owpackage.name,self.owpackage.version)

    def __repr__(self):
        return self.__str__()