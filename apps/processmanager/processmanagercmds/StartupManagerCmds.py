from JumpScale import j


class StartupManagerCmds():

    def __init__(self,daemon):
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth
        self.manager= j.tools.startupmanager        
        self._name="startupmanager"

    def getDomains(self,**args):
        return self.manager.getDomains()

    def startAll(self,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.startAll()

    def removeProcess(self,domain, name,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.removeProcess(domain, name)

    def getStatus4JPackage(self,jpackage,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.getStatus4JPackage(jpackage)

    def getStatus(self, domain, name,**args):
        """
        get status of process, True if status ok
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.getStatus( domain, name)

    def listProcesses(self,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return [item.split("__") for item in self.manager.listProcesses()]

    def getProcessesActive(self, domain=None, name=None, session=None,**kwargs):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        result = list()
        for pd in self.manager.getProcessDefs(domain, name):
            item = dict()
            item['status'] = pd.isRunning()
            item['pid'] = pd.pid
            item['name'] = pd.name
            item['domain'] = pd.domain
            item['autostart'] = pd.autostart == '1'
            item['cmd'] = pd.cmd
            item['args'] = pd.args
            item['args'] = pd.args
            item['ports'] = pd.ports
            item['priority'] = pd.priority
            item['workingdir'] = pd.workingdir
            item['env'] = pd.env
            result.append(item)
        return result


    def startProcess(self, domain="", name="", timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.startProcess( domain, name, timeout)

    def stopProcess(self, domain,name, timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.stopProcess(domain,name, timeout)

    def disableProcess(self, domain,name, timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.disableProcess( domain,name, timeout)

    def enableProcess(self, domain,name, timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.enableProcess( domain,name, timeout)

    def restartProcess(self, domain,name,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        return self.manager.restartProcess( domain,name)

    def reloadProcess(self, domain, name,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        return self.manager.reloadProcess( domain,name)



