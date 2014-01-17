from JumpScale import j


class StatsCmds():

    def __init__(self,daemon):
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth
        self.manager= j.tools.startupmanager        
        self._name="stats"

    def listStatKeys(self,prefix="",memonly=False,avgmax=False,session=None):        
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return j.system.stataggregator.list(prefix=prefix,memonly=memonly,avgmax=avgmax)

