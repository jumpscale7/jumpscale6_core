from JumpScale import j


class JPackagesCmds():

    def __init__(self,daemon):
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth
        self._name="jpackages"

    def _getJPackage(self, domain, name):
        jps = j.packages.find(domain, name, installed=True)
        if not jps:
            raise RuntimeError('Could not find installed jpackage with domain %s and name %s' % (domain, name))
        return jps[0]


    def listJPackages(self, domain=None, **args):
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

    def getJPackage(self, domain, name, **args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        package = j.packages.findNewest(domain, name, returnNoneIfNotFound=True)
        result = dict()
        fields = ('buildNr', 'debug', 'dependencies','domain',
                  'name', 'startupTime', 'supportedPlatforms',
                  'taskletsChecksum', 'tcpPorts', 'version')
        if package:
            for field in fields:
                result[field] = getattr(package, field)
        return result

    def startJPackage(self,jpackage,timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.startJPackage(jpackage,timeout)

    def stopJPackage(self,jpackage,timeout=20,**args):  
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        return self.manager.stopJPackage(jpackage,timeout)

    def existsJPackage(self,jpackage,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.existsJPackage(jpackage)

