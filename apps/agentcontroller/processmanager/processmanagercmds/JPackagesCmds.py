from JumpScale import j


class JPackagesCmds():

    def __init__(self,daemon=None):
        self._name="jpackages"
        if daemon==None:
            return

        self.daemon=daemon
        self._adminAuth=daemon._adminAuth

        self.manager=j.tools.startupmanager

    def _getJPackage(self, domain, name):
        jps = j.packages.find(domain, name, installed=True)
        if not jps:
            raise RuntimeError('Could not find installed jpackage with domain %s and name %s' % (domain, name))
        return jps[0]


    def listJPackages(self, domain=None, session=None,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        if not domain:
            packages = j.packages.getInstalledPackages()
        else:
             dobj = j.packages.getDomainObject(domain)
             packages = dobj.getJPackages()
        result = list()
        fields = ('name', 'domain', 'version')
        for package in packages:
            if package.isInstalled():
                pdict = dict()
                for field in fields:
                    pdict[field] = getattr(package, field)
                result.append(pdict)
        return result

    def getJPackage(self, domain, name, session=None, **args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        package = j.packages.findNewest(domain, name, returnNoneIfNotFound=True)
        result = dict()
        fields = ('buildNr', 'debug', 'dependencies','domain',
                  'name', 'startupTime', 'supportedPlatforms',
                  'tcpPorts', 'version','tags','version')

        if package:
            for field in fields:
                result[field] = getattr(package, field)

            result['isInstalled'] = package.isInstalled()
            result['codeLocations'] = package.getCodeLocationsFromRecipe()
            result['metadataPath'] = package.getPathMetadata()
            result['filesPath'] = package.getPathFiles()
            recipe=package.getCodeMgmtRecipe()            
            lines=[line for line in j.system.fs.fileGetContents(recipe.configpath).split("\n") if (line.strip()<>"" and line.strip()[0]<>"#")]
            result['coderecipe']="\n".join(lines)
            result['description'] = j.system.fs.fileGetContents("%s/description.wiki"%package.getPathMetadata())
            result["buildNrInstalled"]=package.getHighestInstalledBuildNr()

        return result


    def getJPackageFilesInfo(self,domain, name, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
                    
        package = j.packages.findNewest(domain, name, returnNoneIfNotFound=True)

        aaData = list()
        
        for platform,ttype in package.getBlobPlatformTypes():

            blobinfo = package.getBlobInfo(platform, ttype)
            for entry in blobinfo[1]:
                aaData.append([platform,ttype,entry[1],entry[0]])
        
        return aaData


    def startJPackage(self,domain, name,timeout=20, session=None,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        jpackage=self._getJPackage(domain,name)
                
        return self.manager.startJPackage(jpackage,timeout)

    def stopJPackage(self,domain, name,timeout=20, session=None,**args):  
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        jpackage=self._getJPackage(domain,name)
        return self.manager.stopJPackage(jpackage,timeout)

    def existsJPackage(self,domain, name, session=None,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        res= j.packages.find(domain, name)
        if len(res)>0:
            return True
        else:
            return False
        

