#!/usr/bin/env python
from JumpScale import j
import sys
import time
try:
    import ujson as json
except:
    import json
import psutil
import imp
import random
import JumpScale.baselib.taskletengine
from JumpScale.baselib import cmdutils

# Preload libraries
j.system.platform.psutil=psutil
import JumpScale.baselib.graphite
import JumpScale.lib.diskmanager
import JumpScale.baselib.stataggregator
import JumpScale.grid.agentcontroller
import JumpScale.baselib.redis
import JumpScale.baselib.redisworker
import JumpScale.grid.jumpscripts

import sys
import os

def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)


class Worker(object):

    def __init__(self, redisaddr, redisport, queuename,name):
        self.actions={}
        self.redisport=redisport
        self.redisaddr=redisaddr
        self.queuename=queuename
        self.name=name
        self.clients = dict()


        self.acclient = None

        self.init()

    def getClient(self, job):
        ipaddr = getattr(job, 'achost', None)
        client = self.clients.get(ipaddr)
        if not client:
            if ipaddr:
                client = j.clients.agentcontroller.get(ipaddr)
                self.clients[ipaddr] = client
            else:
                if self.acclient==None:
                    self.acclient=j.clients.agentcontroller.getByInstance('main')
                return self.acclient
        return client

    def init(self):

        j.system.fs.createDir(j.system.fs.joinPaths(j.dirs.tmpDir,"jumpscripts"))

        self.redisprocessmanager=j.clients.credis.getRedisClient('127.0.0.1', 7766)

        def checkredis():
            success=False
            wait=1
            while success==False:
                try:
                    self.redis = j.clients.credis.getRedisClient(self.redisaddr, self.redisport)
                    success=True
                except Exception,e:
                    msg="Cannot connect to redis on %s:%s, will retry."%(self.redisaddr,self.redisport)
                    print msg
                    j.events.opserror(msg, category='worker.startup', e=e)
                    if wait<60:
                        wait+=1
                    time.sleep(wait)

        checkredis()
        self.redisprocessmanager.delete("workers:action:%s"%self.name)

        #@todo check if queue exists if not raise error
        self.queue=j.clients.credis.getRedisQueue(opts.addr, opts.port, "workers:work:%s" % self.queuename)

    def run(self):
        print "STARTED"
        w=j.clients.redisworker
        w.useCRedis()
        while True:

            ############# PROCESSMANAGER RELATED 
            #check if we need to restart
            if self.redisprocessmanager.exists("workers:action:%s"%self.name):
                if self.redisprocessmanager.get("workers:action:%s"%self.name)=="STOP":
                    print "RESTART ASKED"
                    self.redisprocessmanager.delete("workers:action:%s"%self.name)
                    restart_program()
                    j.application.stop()

                if self.redis.get("workers:action:%s"%self.name)=="RELOAD":
                    print "RELOAD ASKED"
                    self.redisprocessmanager.delete("workers:action:%s"%self.name)
                    self.actions={}

            self.redisprocessmanager.hset("workers:watchdog",self.name,int(time.time()))
            ################ END PROCESS MANAGER


            try:
                # print "check if work", comes from redis
                job=w._getWork(self.queuename,timeout=4)
            except Exception,e:
                if str(e).find("Could not find queue to execute job")<>-1:
                    #create queue
                    print "could not find queue:%s"%self.queuename
                else:
                    j.events.opserror("Could not get work from redis, is redis running?","workers.getwork",e)
                time.sleep(10)
                continue

            if job:
                j.application.jid=job.id

                if self.actions.has_key(job.jscriptid):
                    jscript=self.actions[job.jscriptid]
                else:
                    print "JSCRIPT CACHEMISS"
                    try:
                        jscript=w.getJumpscriptFromId(job.jscriptid)

                        if jscript==None:
                            msg="cannot find jumpscript with id:%s"%job.jscriptid
                            print "ERROR:%s"%msg
                            j.events.bug_warning(msg,category="worker.jscript.notfound")
                            job.result=msg
                            job.state="ERROR"
                            self.notifyWorkCompleted(job)
                            continue

                        if jscript.organization<>"" and jscript.name<>"" and jscript.id<1000000:
                            #this is to make sure when there is a new version of script since we launched this original script we take the newest one
                            jscript=w.getJumpscriptFromName(jscript.organization,jscript.name)
                            job.jscriptid=jscript.id
                            #result is method action

                        jscript.write()
                        jscript.load()

                        self.actions[job.jscriptid]=jscript

                    except Exception,e:
                        agentid=j.application.getAgentId()
                        msg="could not compile jscript:%s %s_%s on agent:%s.\nError:%s"%(jscript.id,jscript.organization,jscript.name,agentid,e)
                        eco=j.errorconditionhandler.parsePythonErrorObject(e)
                        eco.errormessage = msg
                        eco.code=jscript.source
                        eco.jid = job.id
                        eco.category = 'workers.compilescript'
                        j.errorconditionhandler.processErrorConditionObject(eco)
                        job.state="ERROR"
                        eco.tb = None
                        job.result=eco.__dict__
                        # j.events.bug_warning(msg,category="worker.jscript.notcompile")
                        # self.loghandler.logECO(eco)
                        self.notifyWorkCompleted(job)
                        continue

                    self.actions[job.jscriptid]=jscript

                self.log("Job started:%s script: %s %s/%s"%(job.id, jscript.id,jscript.organization,jscript.name))

                j.logger.enabled = job.log
                status, result=jscript.executeInWorker(**job.args)
                j.logger.enabled = True
                if status:
                    job.result=result
                    job.state="OK"
                    job.resultcode=0
                else:
                    eco = result
                    agentid=j.application.getAgentId()
                    msg="Could not execute jscript:%s %s_%s on agent:%s\nError: %s"%(jscript.id,jscript.organization,jscript.name,agentid, eco.errormessage)
                    eco.errormessage = msg
                    eco.jid = job.id
                    eco.code=jscript.source
                    eco.category = "workers.executejob"

                    out=""
                    tocheck=["\"worker.py\"","jscript.executeInWorker","return self.module.action","JumpscriptFactory.py"]
                    for line in eco.backtrace.split("\n"):
                        found=False
                        for check in tocheck:
                            if line.find(check)<>-1:
                                found=True
                                break
                        if found==False:
                            out+="%s\n"%line

                    eco.backtrace=out

                    if job.id<1000000 and job.errorreport==True:
                        j.errorconditionhandler.processErrorConditionObject(eco)
                    else:
                        print eco.errormessage
                    # j.events.bug_warning(msg,category="worker.jscript.notexecute")
                    # self.loghandler.logECO(eco)
                    job.state="ERROR"
                    eco.tb = None
                    job.result=eco.__dict__
                    job.resultcode=1

                #ok or not ok, need to remove from queue test
                #thisin queue test is done to now execute script multiple time
                self.redis.hdel("workers:inqueuetest",jscript.getKey())

                self.notifyWorkCompleted(job)


    def notifyWorkCompleted(self,job):
        acclient = self.getClient(job)
        w=j.clients.redisworker
        job.timeStop=int(time.time())

        # if job.state[0:2]<>"OK":
        #     self.log("result:%s"%job.result)


        if job.jscriptid>1000000:
            #means is internal job
            # q=j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:return:%s"%jobid)
            self.redis.hset("workers:jobs",job.id, json.dumps(job.__dict__))
            w.redis.rpush("workers:return:%s"%job.id,time.time())            
        else:
            #jumpscripts coming from AC
            if job.state<>"OK":
                try:
                    acclient.notifyWorkCompleted(job.__dict__)
                except Exception,e:
                    j.events.opserror("could not report job in error to agentcontroller", category='workers.errorreporting', e=e)
                    return
                #lets keep the errors
                # self.redis.hdel("workers:jobs",job.id)
            else:
                if job.log or job.wait:
                    try:
                        acclient.notifyWorkCompleted(job.__dict__)
                    except Exception,e:
                        j.events.opserror("could not report job result to agentcontroller", category='workers.jobreporting', e=e)
                        return
                    # job.state=="OKR" #means ok reported
                    #we don't have to keep status of local job result, has been forwarded to AC
                self.redis.hdel("workers:jobs",job.id)


    def log(self, message, category='',level=5):
        #queue saving logs        
        # j.logger.log(message,category=category,level=level)
        print message


if __name__ == '__main__':
    parser = cmdutils.ArgumentParser()
    parser.add_argument("-wn", '--workername', help='Worker name')
    parser.add_argument("-qn", '--queuename', help='Queue name', required=True)
    parser.add_argument("-pw", '--auth', help='Authentication of redis')
    parser.add_argument("-a", '--addr', help='Address of redis',default="127.0.0.1")
    parser.add_argument("-p", '--port', type=int, help='Port of redis',default=7768)
    parser.add_argument('--nodeid', type=int, help='nodeid, is just to recognise the command in ps ax',default=0)

    opts = parser.parse_args()

    wait=1
    while j.system.net.tcpPortConnectionTest("127.0.0.1",7766)==False:
        msg= "cannot connect to redis main, will keep on trying forever, please start redis process manager (port 7766)"    
        print msg
        j.events.opserror(msg, category='worker.startup')    
        if wait<60:
            wait+=1
        time.sleep(wait)

    rediscl = j.clients.credis.getRedisClient('127.0.0.1', 7766)
    rediscl.hset("workers:watchdog",opts.workername,0) #now the process manager knows we got started but maybe waiting on other requirements

    wait=1
    while j.system.net.tcpPortConnectionTest("127.0.0.1",7768)==False:
        time.sleep(wait)
        msg= "cannot connect to redis, will keep on trying forever, please start redis production (port 7768)"
        print msg
        j.events.opserror(msg, category='worker.startup')        
        if wait<60:
            wait+=1

    j.application.start("jumpscale:worker")

    if j.application.config.exists("grid.id"):
        j.application.initGrid()

    j.logger.consoleloglevel = 2
    j.logger.maxlevel=7

    worker=Worker(opts.addr, opts.port, opts.queuename,name=opts.workername)
    worker.run()

