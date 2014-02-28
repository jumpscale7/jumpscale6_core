from JumpScale import j

import importlib
import sys


class Empty():
    pass


class AAProcessManagerCmds():

    def __init__(self, daemon=None):

        self._name="pm"

        self.daemon = daemon
        j.processmanager=self

        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = 'root'#j.application.config.get('system.superadmin.login')

        if daemon<>None:
            self.daemon._adminAuth=self._adminAuth
            masterip=j.application.config.get("grid.master.ip")
            self.daemon.osis = j.core.osis.getClient(masterip, user='root')
        
        
        

    def _init(self):

        self.childrenPidsFound={} #children already found, to not double count


    def getMonitorObject(self,name,id,monobject=None,lastcheck=0,session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        if not j.core.processmanager.monObjects.__dict__.has_key(name):
            raise RuntimeError("Could not find factory for monitoring object:%s"%name)

        if lastcheck==0:
            lastcheck=time.time()
        val=j.core.processmanager.monObjects.__dict__[name].get(id,monobject=monobject,lastcheck=lastcheck)
        if session<>None:
            return val.__dict__
        else:
            return val

    def exit(self,session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        j.application.stop()

    def _adminAuth(self,user,passwd):
        if user != self.adminuser or passwd != self.adminpasswd:
            raise RuntimeError("permission denied")           



                        