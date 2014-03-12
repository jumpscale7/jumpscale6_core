from JumpScale import j


class ProcessCmds():

    def __init__(self,daemon=None):
        self._name="process"

        if daemon==None:
            return

        self.daemon=daemon
        self._adminAuth=daemon._adminAuth

    def getProcessObjFromSystemPid(self,pid,session=None):
        #no security required, everyone can ask this
        data= j.core.processmanager.monObjects.processobject.getFromSystemPid(pid)
        if data==None:
            return None
        return data.__dict__

    def registerProcess(self,pid,domain,name,workingdir="",session=None):
        j.core.processmanager.monObjects.processobject.pid2name[pid]=(domain,name)
        if domain==None:
            process_key="%s_%s"%(domain,name)
        else:
            process_key="%s"%(name)

        print "new process: '%s' pid:'%s'"%(process_key,pid)

        cacheobj=j.core.processmanager.monObjects.processobject.get(id=process_key)
        cacheobj.db.active=True
        cacheobj.db.sname = name
        cacheobj.db.pname = name
        cacheobj.db.jpdomain=domain
        cacheobj.db.type="js"
        cacheobj.db.getSetGuid()
        cacheobj.db.workingdir=workingdir
        guid,tmp,tmp=cacheobj.send2osis()
        return guid

    def checkHeartbeat(self, session=None):
        nid = j.application.whoAmI.nid
        gid = j.application.whoAmI.gid

        hearbeat = j.core.processmanager.monObjects.heartbeatobject.get('%s_%s' % (gid, nid))
        lastchecked = hearbeat.lastcheck
        now = j.base.time.getTimeEpoch()

        if  now - j.base.time.getEpochAgo('-2m') > now - lastchecked:
            return True
        return False
    
                        