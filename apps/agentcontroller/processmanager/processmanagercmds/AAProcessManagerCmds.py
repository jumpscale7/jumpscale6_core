from JumpScale import j

import importlib
import sys
import fcntl
import os

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
        
        
    def stop(self,session=None):
        print "STOP PROCESS MANAGER\n\n\n\n\n"

        if session<>None:
            self._adminAuth(session.user,session.passwd)
        # raise RuntimeError("STOP APPLICATION 112299")
        args = sys.argv[:]
        args.insert(0, sys.executable)
        max_fd = 1024
        for fd in range(3, max_fd):
            try:
                flags = fcntl.fcntl(fd, fcntl.F_GETFD)
            except IOError:
                continue
            fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
        os.chdir("%s/apps/processmanager/"%j.dirs.baseDir)
        os.execv(sys.executable, args)

    def reloadjumpscripts (self,session=None):
        print "RELOAD JUMPSCRIPTS\n\n\n\n\n"
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        s=self.daemon.cmdsInterfaces["jumpscripts"]
        s.loadJumpscripts()

        s=self.daemon.cmdsInterfaces["worker"] #this will make sure workers reload
        s.reloadWorkers()

    def restartWorkers(self,session=None):
        print "RESTART WORKERS\n\n\n\n\n"
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        s=self.daemon.cmdsInterfaces["worker"] #this will make sure workers reload
        s.stopWorkers()            

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



                        