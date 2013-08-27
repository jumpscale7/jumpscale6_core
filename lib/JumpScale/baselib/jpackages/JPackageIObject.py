from JumpScale import j

class JPackageIObject:
    
    def __init__(self, jpackages):
        self.jpackages = jpackages
        self.setDebugMode = jpackages.setDebugMode
        self.getDebugMode = jpackages.getDebugMode
        self.removeDebugMode = jpackages.removeDebugMode
        self.prepareForUpdatingFiles = jpackages.prepareForUpdatingFiles
        self.getBrokenDependencies = jpackages.getBrokenDependencies
        self.getDependencyTree = jpackages.getDependencyTree
        self.getBuildDependencyTree = jpackages.getBuildDependencyTree
        self.getRuntimeDependencyTree = jpackages.getRuntimeDependencyTree
        self.install = jpackages.install
        self.reload = jpackages.load
        self.delete = jpackages.delete
        self.upload = jpackages.upload
        self.codeCommit = jpackages.codeCommit
        self.codeExport = jpackages.codeExport
        self.codeImport = jpackages.codeImport
        self.codeLink = jpackages.codeLink
        self.codePush = jpackages.codePush
        self.codeUpdate = jpackages.codeUpdate

    #def quickPackage(self):
        #"""
        #The following process will be followed
        #- checkout code -> sandbox
        #- build code (if needed)
        #- package code -> jpackages files directory
        #when ready to quickPackage your jpackages you will still have to do a i.qp.publishAll()
        #"""
        #self.jpackages.prepareForUpdatingFiles(False)
        #self.jpackages.checkout()
        #self.jpackages.compile()
        #self.jpackages.package()
        ##i.qp.publishDomain(self.package.domain)
        
    def _printList(self, arr):
        for item in arr:
            j.console.echo(item)        
    
    def showDependencies(self):
        """
        Return all dependencies of the JPackage.
        See also: addDependency and removeDependency
        """
        
        platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")
        recursive = j.console.askYesNo("Recursive?")
        self._printList(self.jpackages.getDependencies(platform, recursive))
        
    def showBuildDependencies(self):
        """
        Return the build dependencies of the JPackage.
        See also: addDependency and removeDependency
        """
        
        ##self.assertAccessable()
        platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")
        recursive = j.console.askYesNo("Recursive?")
        self._printList(self.jpackages.getBuildDependencies(platform, recursive))
        
    def showRuntimeDependencies(self):
        """
        Return the runtime dependencies of the JPackage.
        See also: addDependency and removeDependency
        """
        
        ##self.assertAccessable()
        platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")
        recursive = j.console.askYesNo("Recursive?")
        self._printList(self.jpackages.getRuntimeDependencies(platform, recursive))
    
    def showDependingInstalledPackages(self):
        """
        Show which jpackages have this jpackages as dependency.
        Do this only for the installed jpackages.
        """
        
        ##self.assertAccessable()
        recursive = j.console.askYesNo("Recursive?")
        self._printList(self.jpackages.getDependingInstalledPackages(recursive))

    def showDependingPackages(self):
        """
        Show which jpackages have this jpackages as dependency.
        """

        ##self.assertAccessable()
        platform = j.console.askChoice(j.enumerators.PlatformType.ALL, "Please select a platform")
        recursive = j.console.askYesNo("Recursive?")
        self._printList(self.jpackages.getDependingPackages(recursive, platform))

    def backup(self):
        """
        Make a backup for this package by running its backup tasklet.
        """
        
        ##self.assertAccessable()
        url = j.console.askString("Url to backup to?")
        self.jpackages.backup(url)
        
    def restore(self):
        """
        Restore a jpackages from specified url by running its restore tasklet.
        """
        
        url = j.console.askString("Url to restore from?")
        self.jpackages.restore(url)


    def packageupload(self, platform=False):
        self.package(platform)
        self.upload()
        
        
    def configure(self):
        """
        Configure this jpackages by running its checkout tasklet.
        """
        
        ##self.assertAccessable()
        #dependencies = j.console.askYesNo("Do you want the dependencies to be configured too?")
        self.jpackages.configure()

    def start(self):
        """
        Start the JPackage by running the start tasklet.
        """
        
        self.jpackages.start()


    def stop(self):
        """
        Stop the JPackage by running the stop tasklet.
        """

        self.jpackages.stop()


    def package(self, platform=False):
        """
        Package this JPackage by running its package tasklet.
        """
        
        if platform == False and len(self.jpackages.supportedPlatforms) == 1:
            platform = self.jpackages.supportedPlatforms[0]
        
        while not platform: 
            platform = j.gui.dialog.askChoice("Select platform. If multiple platforms please quit, is not supported.", j.enumerators.PlatformType.ALL)    
        self.jpackages.package(platform=platform)
     
          
    def reinstall(self, dependencies=False, download=True):
        """
        Reinstall the JPackage by running its install tasklet, best not to use dependancies reinstall 
        """        
        self.jpackages.install(dependencies=dependencies, download=download, reinstall=True)
          
        
    def download(self):
        """
        Download the bundle of this package from the bundle server through ftp as specified in the bundledownload property of the domain of this package.
        This is the invers operation from upload.
        """
        
        ##self.assertAccessable()
        dependencies = j.console.askYesNo("Do you want the bundles of all depending packages to be downloaded too?")
        self.jpackages.download(dependencies)


    def getDescription(self):
        """
        Return the description of this package.
        """

        ##self.assertAccessable()
        return self.jpackages.description

    def __str__(self):
        #if not self.jpackages.assertAccessable():
        return "IPackage %s %s %s" % (self.jpackages.domain, self.jpackages.name, self.jpackages.version)
        #else:
        #    return "Deleted IPackage %s %s %s" % (self.jpackages.domain,self.jpackages.name,self.jpackages.version)

    def __repr__(self):
        return self.__str__()