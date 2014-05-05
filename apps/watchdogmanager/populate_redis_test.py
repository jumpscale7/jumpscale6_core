try:
    import ujson as json
except:
    import json

from JumpScale import j

import JumpScale.baselib.watchdog.manager

j.application.start("jumpscale:alermanager:populate")

gridguids=['6c336b0b900d482c8fad8b160d19414d','087df0f164884ca38b1e38bf470d9ca4','991dc66d1a3e42ada608ba7c994da1ab']
categories=["cpu.core","cpu.contextswitch","disk.full","machine.status","disk.mirror","grid.healthcheck"]
states=["CRITICAL", "WARNING"]

cl=j.tools.watchdogmanager.redis

def getGridGuid():
    grid=j.base.idgenerator.generateRandomInt(0,len(gridguids)-1)+4
    nid=j.base.idgenerator.generateRandomInt(1,30)
    return gid,nid,gridguids[grid]

def getCategoryValue(category=None):
    if category==None:
        i=j.base.idgenerator.generateRandomInt(0,len(categories)-1)
        category=categories[i]
    if category=="cpu.core":
        val=j.base.idgenerator.generateRandomInt(1,100)
    elif category=="cpu.contextswitch":
        val=j.base.idgenerator.generateRandomInt(1,40000)
    elif category=="disk.full":
        val=j.base.idgenerator.generateRandomInt(1,100)
    elif category=="machine.status":
        val=0
    elif category=="disk.mirror":
        val=0
    elif category=="grid.healthcheck":
        val=0
    else:
        raise RuntimeError("not found")
    return val,category

def getState():
    i=j.base.idgenerator.generateRandomInt(0,len(states)-1)
    return states[i]

nrperiods=1
start=j.base.time.getTimeEpoch()-nrperiods*15*60 #per 15 min an wde
stop=j.base.time.getTimeEpoch()

curs=start
intervals=[]
while curs<stop:
    curs+=15*60
    intervals.append(curs)

def getEpoch():
    i=j.base.idgenerator.generateRandomInt(0,len(intervals)-1)
    return intervals[i]

def initalLoad():
    print "initialload"
    curs=start
    while curs<stop:
        curs+=15*60
        for gguid in gridguids:
            gid=gridguids.index(gguid)
            for category in categories:
                print category
                state="OK"
                if category=="grid.healthcheck":
                    nid=0
                    value,category=getCategoryValue(category)
                    wde=j.tools.watchdogmanager.getWatchDogEventObj(gid,nid,category,state,value,gguid)
                    wde.epoch=curs
                    j.tools.watchdogmanager.setWatchdogEvent(wde,pprint=True)
                else:
                    for nid in range(1,30):
                        value,category=getCategoryValue(category)
                        wde=j.tools.watchdogmanager.getWatchDogEventObj(gid,nid,category,state,value,gguid)
                        wde.epoch=curs
                        j.tools.watchdogmanager.setWatchdogEvent(wde,pprint=True)

def errorsLoad():
    print "ERRORSLOAD"
    guids=j.tools.watchdogmanager.getGGUIDS()
    #errors
    for i in range(10):
        i2=j.base.idgenerator.generateRandomInt(0,len(guids)-1)
        gguid=guids[i2]
        keys=cl.hkeys("%s:watchdogevents"%gguid)
        i3=j.base.idgenerator.generateRandomInt(0,len(keys)-1)
        wdekey=keys[i3]
        nid,category=wdekey.split("_")
        wde=j.tools.watchdogmanager.getWatchdogEvent(gguid,nid,category)
        wde.state=getState()
        j.tools.watchdogmanager.setWatchdogEvent(wde,pprint=True)
    #watchdogfailures
    for i in range(2):
        i2=j.base.idgenerator.generateRandomInt(0,len(guids)-1)
        gguid=guids[i2]
        keys=cl.hkeys("%s:watchdogevents"%gguid)
        i3=j.base.idgenerator.generateRandomInt(0,len(keys)-1)
        nid,category=wdekey.split("_")
        wde=j.tools.watchdogmanager.getWatchdogEvent(gguid,nid,category)
        wde.state="OK"
        wde.epoch=wde.epoch-15*7*60 #put 7 periods back
        j.tools.watchdogmanager.setWatchdogEvent(wde,pprint=True)


j.tools.watchdogmanager.reset()

initalLoad()
errorsLoad()

j.application.stop()

