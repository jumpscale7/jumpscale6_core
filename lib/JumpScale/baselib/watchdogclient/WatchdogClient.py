from JumpScale import j

import JumpScale.baselib.webdis

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


try:
    import ujson as json
except:
    import json


class WatchdogClient:
    def __init__(self):

        addr=j.application.config.get("grid.watchdog.addr", checkExists=True)
        if addr==False or addr=="":
            raise RuntimeError("please configure grid.watchdog.addr in hrdconfig")

        secret=j.application.config.get("grid.watchdog.secret", checkExists=True)
        if secret==False or secret=="":
            raise RuntimeError("please configure grid.watchdog.secret in hrdconfig")
        self.secret=secret
        
        self.webdis=j.clients.webdis.get(addr=addr, port=7779, timeout=1)

    def _getWatchDogEventObj(self,gid=0,nid=0,category="",state="",value=0,gguid="",ecoguid="",ddict={}):
        return WatchdogEvent(gid,nid,category,state,value,ecoguid,gguid=self.secret,ddict=ddict)

    def _getWatchDogHSetKey(self,gguid):
        return "%s:watchdogevents"%gguid

    def _setWatchdogEvent(self,wde,pprint=False):
        obj=json.dumps(wde.__dict__)
        res=self.webdis.hset(self._getWatchDogHSetKey(wde.gguid),"%s_%s"%(wde.nid,wde.category),obj)
        if pprint:
            print wde        
        return res

    def send(self,category,state,value,ecoguid=""):
        wde=self._getWatchDogEventObj(j.application.whoAmI.gid,j.application.whoAmI.nid,category,state,value,ecoguid)
        return self._setWatchdogEvent(wde)


