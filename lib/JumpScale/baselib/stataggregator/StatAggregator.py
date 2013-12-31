
from JumpScale import j

import time

class Stat():
    def __init__(self,period=3600):
        self.results={}
        self.result=0
        self.period=period

    def set(self,now,val,remember=True):        
        self.result=val
        if remember:
            self.results[now]=val
        return val

    def getAvgMax(self):
        """
        @return (avg,max)
        """
        tot=0.0
        nr=0
        m=0 #max
        for key in self.results.keys():
            tot+=self.results[key]
            nr+=1
            if self.results[key]>m:
                m=self.results[key]
        return (round(tot/nr,2),m)

    def clean(self,now):
        for key in self.results.keys():
            if key<now-self.period:
                self.results.pop(key)

class StatDiffPerSec(Stat):
    def __init__(self,period=3600):
        Stat.__init__(self,period)
        self.lastPoll=0
        self.lastVal=0

    def set(self,now,val,remember=True):        
        if self.lastPoll==0:
            result=0
        else:
            period=now-self.lastPoll
            result=round((val-self.lastVal)/period,2)*100

        self.lastPoll=now
        self.lastVal=val
        self.result=result
        if remember:
            self.results[now]=result
     
        return result
                

class StatAggregator():

    def __init__(self):
        self.stats={}

    def getTime(self):
        return time.time()

    def set(self,key,val,remember=True):
        
        val=float(val)
        if not self.stats.has_key(key):
            self.registerStats(key)
        result=self.stats[key].set(self.getTime(),val,remember=remember)
        print "set:%s:%s result:%s"%(key,val,result)
        return result

    def get(self,key):
        if not self.stats.has_key(key):
            raise RuntimeError("Could not find stat with key:%s"%key)
        return self.stats[key].result

    def getAvgMax(self,key):
        if not self.stats.has_key(key):
            raise RuntimeError("Could not find stat with key:%s"%key)
        return self.stats[key].getAvgMax()

    def registerStats(self,key):

        if key.find("percent")<>-1 or key.find("space")<>-1 \
            or key.find("memory")<>-1 \
            or key.find("swap")<>-1 \
            or key.find("contentswitches")<>-1 \
            or key.find("openfiles")<>-1:
            self.stats[key]=Stat()
        else:            
            self.stats[key]=StatDiffPerSec()

    def clean(self):
        for key in self.stats:
            stat=self.stats[key]
            stat.clean(self.getTime())

    def send2carbon(self):
        out=""
        for key in self.stats.keys():
            stat=self.stats[key]
            out+="%s.last %s\n" %(key,stat.result)
            avg,m=stat.getAvgMax()
            out+="%s.avg %s\n" %(key,avg)
            out+="%s.max %s\n" %(key,m)
        j.clients.graphite.send(out)
        print out






