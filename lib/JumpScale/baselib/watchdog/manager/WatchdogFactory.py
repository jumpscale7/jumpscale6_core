from JumpScale import j
import imp
import time
import JumpScale.baselib.hash

try:
    import ujson as json
except:
    import json

import JumpScale.baselib.credis
#from JumpScale.baselib.watchdog import WatchdogEvent
import JumpScale.baselib.watchdog as watchdog

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


class WatchdogFactory:
    def __init__(self):
        # while j.system.net.tcpPortConnectionTest("127.0.0.1",9999)==False:
        #     time.sleep(0.1)
        #     print "cannot connect to redis production, will keep on trying forever, please start redis production (port 9999)"        
        self.redis = j.clients.redis.getByInstanceName('system')
        self.watchdogTypes={}
        self.alertTypes={}
        self._getWatchDogTypes()
        self._getAlertTypes()
        # self.localgguid="dfsdfadsfasdffg"  #temp

    # def getWatchDogEventObj(self,gid=0,nid=0,category="",state="",value=0,gguid="",ecoguid="",ddict={}):
    #     return WatchdogEvent(gid,nid,category,state,value,ecoguid,gguid=gguid,ddict=ddict)

    # def getWatchdogType(self,category="",alertperiod=17*60,ddict={}):
    #     return WatchdogType(category,alertperiod,ddict)

    def setWatchdogEvent(self, alert, pprint=True):
        res = self.rediscl.hset(watchdog.getHSetKey(alert.gid), "%s_%s" % (alert.nid, alert.category), alert)
        if pprint:
            print alert
        return res

    def _getAlertHSetKey(self, gid):
        return "alerts:%s" % gid

    def _getWatchDogTypes(self):
        jspath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'watchdogmanager', 'watchdogtypes')
        if j.system.fs.exists(jspath):
            for jscriptpath in j.system.fs.listFilesInDir(path=jspath, recursive=True, filter="*.py", followSymlinks=True):
                wdt = WatchdogType(path=jscriptpath)
                self.watchdogTypes[wdt.category] = wdt
        else:
            raise RuntimeError("could not find:%s" % jspath)  

    def _getAlertTypes(self):
        jspath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'watchdogmanager', 'alerttypes')
        if j.system.fs.exists(jspath):
            for jscriptpath in j.system.fs.listFilesInDir(path=jspath, recursive=True, filter="*.py", followSymlinks=True):
                if j.system.fs.getBaseName(jscriptpath)[0]=="_":
                    continue
                at = AlertType(path=jscriptpath)
                self.alertTypes[at.name] = at
        else:
            raise RuntimeError("could not find:%s" % spath)  

    def getWatchdogType(self, category):
        if category not in self.watchdogTypes:
            self.alert("bug in watchdogmanager: could not find watchdogtype:%s"%category,"critical")
        return self.watchdogTypes[category]

    def getAlertType(self, name):
        if not self.alertTypes.has_key(name):
            self.alert("bug in watchdogmanager: could not find alerttype:%s"%name,"critical")
        return self.alertTypes[name]

    def checkWatchdogEvent(self, alert):
        wdt = self.getWatchdogType(alert.category)
        try:
            wdt.checkfunction(alert)
        except Exception,e:
            self.alert("bug in watchdogmanager: could not process watchdogcheck:%s, error %s"%(wdt,e),"critical")
        if alert.state != "OK":
            self.alert("STATE","critical",alert)
        if alert.epoch<(time.time() - wdt.maxperiod):
            alert.state="TIMEOUT"
            self.setAlert(alert)
            self.alert("TIMEOUT","critical",alert)

    def alert(self, alerttype, alert):
        at=self.getAlertType(alerttype)
        if self.inAlert(alert):
            return
        at.escalateL1(alert)

    def checkWatchdogEvents(self):
        for gguid in self.getGGUIDS():
            for wde in self.iterateWatchdogEvents(gguid):
                self.checkWatchdogEvent(wde)

    def inAlert(self, alert):
        key = "%s_%s" % (alert.nid, alert.category)
        return self.redis.hexists(self._getAlertHSetKey(alert.gid), key)

    def setAlert(self, alert):
        key = "%s_%s" % (alert.nid, alert.category)
        wde.escalationepoch=time.time()
        self.setWatchdogEvent(wde)
        return self.redis.hset(self._getAlertHSetKey(wde.gguid),key, json.dumps(wde.__dict__))

    def getAlert(self,gguid,nid,category):
        wde=self.getWatchdogEvent(gguid,nid,category)
        if not self.inAlert(wde):
            self.alert("bug in watchdogmanager: could not find alert:%s"%wde,"critical")
            return None
        return wde

    def iterateAlerts(self,gguid):
        for key in self.redis.hkeys(self._getAlertHSetKey(gguid)):
            nid,category=key.split("_",1)
            yield self.getAlert(gguid,nid,category)            

    def deleteAlert(self, wde):
        key = "%s_%s" % (wde.nid, wde.category)
        return self.redis.hdel(self._getAlertHSetKey(wde.gguid), key)

    def iterateWatchdogEvents(self,gguid):
        for key in self.redis.hkeys(watchdog.getHSetKey(gguid)):
            nid,category=key.split("_")
            yield self.getWatchdogEvent(gguid,nid,category)

    def getWatchdogEvent(self,gguid,nid,category):
        key="%s_%s"%(nid,category)
        obj=json.loads(self.redis.hget(watchdog.getHSetKey(gguid),key))
        wde=WatchdogEvent(ddict=obj)
        return wde

    def getGGUIDS(self):
        """
        each grid has unique guid called gguid
        return from local ssdb or redis the grid guids
        """
        return [item.split(":")[1] for item in self.redis.keys("watchdogevents:*") ]

    def reset(self):
        """
        resets all watchdogs
        """
        print "reset"
        for gguid in self.getGGUIDS():
            self.redis.delete(watchdog.getHSetKey(gguid))

    def _log(self,msg,category="",level=5):
        if level<self.loglevel+1 and self.logenable:
            j.logger.log(msg,category="watchdog.%s"%category,level=level)

    #DONT DO THIS, TOOOOO MEM HUNGRY
    # def fetchAllAlerts(self):
    #     gguids = self.getGGUIDS()
    #     result = dict()
    #     for gguid in gguids:
    #         result.update(self.redis.hgetall(self._getAlertHSetKey(gguid)))
    #     return [json.loads(wde) for wde in result.values()]


