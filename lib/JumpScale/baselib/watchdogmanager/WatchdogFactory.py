from JumpScale import j


from .WatchdogManager import *
import imp
import JumpScale.baselib.hash

class WatchdogEvent:
    def __init__(self,gid=0,nid=0,category="",state="",value=0,ecoguid="",gguid="",ddict={}):
        if ddict<>{}:
            self.__dict__=ddict
        else:
            self.gguid=gguid
            self.nid=nid
            self.gid=gid
            self.category=category
            self.state=state
            self.value=value
            self.ecoguid=""
            self.epoch=j.base.time.getTimeEpoch()
            self.escalationstate=""
            self.escalationepoch=0
            self.log=[]

    def __str__(self):
        dat=j.base.time.epoch2HRDateTime(self.epoch)
        return "%s %s %s %-30s %-10s %s"%(dat,self.gid,self.nid,self.category,self.state,self.value)

    __repr__=__str__


class WatchdogType():
    def __init__(self,path):
        self.path=path
        md5sum = j.tools.hash.md5_string(self.path)
        modulename = 'JumpScale.watchdogtype_%s' % md5sum
        self.module = imp.load_source(modulename, self.path)
        name = getattr(self.module, 'name', "")
        if name=="":
            name=j.system.fs.getBaseName(self.path)
            name=name.replace(".py","").lower()
        self.category=name
        self.descr=self.module.descr.lstrip()
        self.maxperiod=getattr(self.module, 'maxperiod',0)
        self.enable=getattr(self.module, 'enable', True) 
        self.organization=getattr(self.module, 'organization', "unknown")
        self.checkfunction=self.module.check

    def __str__(self):
        return "%-50s %s"%(self.category,self.maxperiod)

    __repr__=__str__

class AlertType():
    def __init__(self,path):
        self.path=path
        md5sum = j.tools.hash.md5_string(self.path)
        modulename = 'JumpScale.alerttype_%s' % md5sum
        self.module = imp.load_source(modulename, self.path)
        name = getattr(self.module, 'name', "")
        if name=="":
            name=j.system.fs.getBaseName(self.path)
            name=name.replace(".py","").lower()
        self.name=name
        self.descr=self.module.descr.lstrip()
        self.enable=getattr(self.module, 'enable', True) 
        self.organization=getattr(self.module, 'organization', "unknown")
        self.escalateL1=self.module.escalateL1
        self.escalateL2=self.module.escalateL2
        self.escalateL3=self.module.escalateL3

    def __str__(self):
        return "%-30s %s"%(self.name,self.enable)

    __repr__=__str__

try:
    import ujson as json
except:
    import json

import JumpScale.baselib.credis

class WatchdogFactory:
    def __init__(self):
        while j.system.net.tcpPortConnectionTest("127.0.0.1",7768)==False:
            time.sleep(0.1)
            print "cannot connect to redis production, will keep on trying forever, please start redis production (port 7768)"        
        self.redis=j.clients.credis.getRedisClient("localhost",7768)
        self.watchdogTypes={}
        self.alertTypes={}
        self._getWatchDogTypes()
        self._getAlertTypes()
        self._now=j.base.time.getTimeEpoch()
        self.localgguid="dfsdfadsfasdffg"  #temp

    def getWatchDogEventObj(self,gid=0,nid=0,category="",state="",value=0,gguid="",ecoguid="",ddict={}):
        return WatchdogEvent(gid,nid,category,state,value,ecoguid,gguid=gguid,ddict=ddict)

    def getWatchdogType(self,category="",alertperiod=17*60,ddict={}):
        return WatchdogType(category,alertperiod,ddict)

    def setWatchdogEvent(self,wde,pprint=True):
        obj=json.dumps(wde.__dict__)
        self.redis.hset(self._getWatchDogHSetKey(wde.gguid),"%s_%s"%(wde.nid,wde.category),obj)
        if pprint:
            print wde

    def _getWatchDogHSetKey(self,gguid):
        return "%s:watchdogevents"%gguid

    def _getAlertHSetKey(self,gguid):
        return "%s:alerts"%gguid

    def _getWatchDogTypes(self):
        jspath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'watchdogmanager', 'watchdogtypes')
        if j.system.fs.exists(jspath):
            for jscriptpath in j.system.fs.listFilesInDir(path=jspath, recursive=True, filter="*.py", followSymlinks=True):
                wdt = WatchdogType(path=jscriptpath)
                self.watchdogTypes[wdt.category]=wdt
        else:
            raise RuntimeError("could not find:%s"%jspath)  


    def _getAlertTypes(self):
        jspath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'watchdogmanager', 'alerttypes')
        if j.system.fs.exists(jspath):
            for jscriptpath in j.system.fs.listFilesInDir(path=jspath, recursive=True, filter="*.py", followSymlinks=True):
                at = AlertType(path=jscriptpath)
                self.alertTypes[at.name]=at
        else:
            raise RuntimeError("could not find:%s"%jspath)  

    def getWatchdogType(self,category):
        if not self.watchdogTypes.has_key(category):
            self.alert("bug in watchdogmanager: could not find watchdogtype:%s"%category,"critical")
        return self.watchdogTypes[category]

    def getAlertType(self,name):
        if not self.alertTypes.has_key(name):
            self.alert("bug in watchdogmanager: could not find alerttype:%s"%name,"critical")
        return self.alertTypes[name]

    def checkWatchdogEvent(self,wde):
        wdt=self.getWatchdogType(wde.category)
        print wde
        print wdt
        try:
            wdt.checkfunction(wde)
        except Exception,e:
            self.alert("bug in watchdogmanager: could not process watchdogcheck:%s, error %s"%(wdt,e),"critical")
        if wde.state<>"OK":
            self.alert("STATE","critical",wde)
        if wde.epoch<(self._now-wdt.maxperiod):
            self.alert("TIMEOUT","critical",wde)

    def alert(self,msg,alerttype,wde=None):
        at=self.getAlertType(alerttype)
        if wde==None:
            wde=self.getWatchDogEventObj(gid=j.application.whoAmI.gid,nid=j.application.whoAmI.nid,\
                category="critical.error",state="ERROR",value=msg,gguid=self.localgguid)
        if self.inAlert(wde):
            return
        at.escalateL1(wde)

    def checkWatchdogEvents(self):
        self._now=j.base.time.getTimeEpoch()
        for gguid in self.getGGUIDS():
            for wde in self.iterateWatchdogEvents(gguid):
                self.checkWatchdogEvent(wde)

    def inAlert(self,wde):
        key="%s_%s"%(wde.nid,wde.category)
        return self.redis.hexists(self._getAlertHSetKey(wde.gguid),key)

    def setAlert(self,wde):
        key="%s_%s"%(wde.nid,wde.category)
        wde.escalationepoch=self._now
        self.setWatchdogEvent(wde)
        return self.redis.hset(self._getAlertHSetKey(wde.gguid),key,"")

    def getAlert(self,gguid,nid,category):
        key="%s_%s"%(nid,category)
        wde=self.getWatchdogEvent(gguid,nid,category)
        if not self.inAlert(wde):
            self.alert("bug in watchdogmanager: could not find alert:%s"%wde,"critical")
            return None
        return wde
        
    def iterateWatchdogEvents(self,gguid):
        for key in self.redis.hkeys(self._getWatchDogHSetKey(gguid)):
            nid,category=key.split("_")
            yield self.getWatchdogEvent(gguid,nid,category)

    def getWatchdogEvent(self,gguid,nid,category):
        key="%s_%s"%(nid,category)
        obj=json.loads(self.redis.hget(self._getWatchDogHSetKey(gguid),key))
        wde=WatchdogEvent(ddict=obj)            
        return wde

    def getGGUIDS(self):
        """
        each grid has unique guid called gguid
        return from local ssdb or redis the grid guids
        """
        return [item.split(":")[0] for item in self.redis.keys() if item.find("watchdogevents")<>-1]

    def reset(self):
        """
        resets all watchdogs
        """
        print "reset"
        for gguid in self.getGGUIDS():
            self.redis.delete(self._getWatchDogHSetKey(gguid))

    def _log(self,msg,category="",level=5):
        if level<self.loglevel+1 and self.logenable:
            j.logger.log(msg,category="watchdog.%s"%category,level=level)


