#!/usr/bin/env python

import sys
import time
import ujson
import psutil
import imp
import random

from JumpScale.baselib import cmdutils
from JumpScale import j

j.application.start("jumpscale:worker")
try:
    print "try to init grid, will not fail if it does not work."
    j.application.initGrid()
except Exception,e:
    print "could not init grid, maybe no osis or work gridless"

# Preload libraries
j.system.platform.psutil=psutil
import JumpScale.baselib.graphite
import JumpScale.lib.diskmanager
import JumpScale.baselib.stataggregator
import JumpScale.grid.agentcontroller
import JumpScale.baselib.redis
import JumpScale.baselib.redisworker

#check redis is there if not try to start
if not j.system.net.tcpPortConnectionTest("127.0.0.1",7768):
    j.packages.findNewest(name="redis").install()
    j.packages.findNewest(name="redis").start()

class Worker(object):

    def __init__(self, redisaddr, redisport, queuename):
        
        self.actions={}
        self.redisport=redisport
        self.redisaddr=redisaddr
        self.queuename=queuename
        self.init()

    def init(self):

        j.system.fs.createDir(j.system.fs.joinPaths(j.dirs.tmpDir,"jumpscripts"))

        def checkagentcontroller():
            masterip=j.application.config.get("grid.master.ip")            
            success=False
            try:
                self.acclient=j.clients.agentcontroller.get(masterip)
                success=True
            except Exception,e:
                msg="Cannot connect to agentcontroller on %s."%(masterip)
                j.events.opserror(msg, category='worker.startup', e=e)
                self.acclient=None


        def checkredis():
            success=False
            while success==False:
                try:
                    self.redis = j.clients.redis.getGeventRedisClient(self.redisaddr, self.redisport)
                    success=True
                except Exception,e:
                    msg="Cannot connect to redis on %s:%s, will retry in 5 sec."%(self.redisaddr,self.redisport)
                    j.events.opserror(msg, category='worker.startup', e=e)
                    time.sleep(5)

        checkredis()
        checkagentcontroller()

        #@todo check if queue exists if not raise error
        self.queue=j.clients.redis.getRedisQueue(opts.addr, opts.port, "workers:work:%s" % self.queuename)

    def _loadModule(self, path):
        '''Load the Python module from disk using a random name'''
        j.logger.log('Loading tasklet module %s' % path, 7)
        # Random name -> name in sys.modules

        def generate_module_name():
            '''Generate a random unused module name'''
            return '_tasklet_module_%d' % random.randint(0, sys.maxint)
        modname = generate_module_name()
        while modname in sys.modules:
            modname = generate_module_name()

        module = imp.load_source(modname, path)
        return module

    def run(self):
        print "STARTED"
        w=j.clients.redisworker
        while True:
            # jobid=self.queue.get()
            # data=self.redis.hget("workerjobs",jobid)
            try:
                # print "check if work", comes from redis
                job=w._getWork(self.queuename,timeout=0)
            except Exception,e:
                j.events.opserror("Could not get work from redis, is redis running?","workers.getwork",e)
                time.sleep(1)
                continue

            if job:
                j.application.jid=job.id
                #eval action code, if not ok send error back, cache the evalled action
                if self.actions.has_key(job.jscriptid):
                    action,jscript=self.actions[job.jscriptid]
                else:
                    print "JSCRIPT CACHEMISS"
                    jscript=w.getJumpscriptFromId(job.jscriptid)

                    if jscript==None:
                        msg="cannot find jumpscript with id:%s"%job.jscriptid
                        print "ERROR:%s"%msg
                        j.events.bug_warning(msg,category="worker.jscript.notfound")
                        job.result=msg
                        job.state="ERROR"
                        self.notifyWorkCompleted(job)
                        continue

                    if jscript.organization<>"" and jscript.name<>"":
                        #this is to make sure when there is a new version of script since we launched this original script we take the newest one
                        jscript=w.getJumpscriptFromName(jscript.organization,jscript.name)
                        job.jscriptid=jscript.id

                    jscriptpath=j.system.fs.joinPaths(j.dirs.tmpDir,"jumpscripts","%s_%s.py"%(jscript.organization,jscript.name))
                    j.system.fs.writeFile(jscriptpath,jscript.source)
                    self.log("Load script:%s %s %s"%(jscript.id,jscript.organization,jscript.name))
                    try:
                        module=self._loadModule(jscriptpath)
                        action=module.action                        
                        #result is method action
                    except Exception,e:
                        agentid=j.application.getAgentId()
                        msg="could not compile jscript:%s %s_%s on agent:%s.\nError:%s"%(jscript.id,jscript.organization,jscript.name,agentid,e)
                        eco=j.errorconditionhandler.parsePythonErrorObject(e)
                        eco.errormessage = msg
                        eco.code=jscript.source
                        eco.jid = job.id
                        eco.category = 'workers.compilescript'
                        j.errorconditionhandler.processErrorConditionObject(eco)
                        # j.events.bug_warning(msg,category="worker.jscript.notcompile")
                        # self.loghandler.logECO(eco)
                        self.notifyWorkCompleted(job)
                        continue

                self.actions[job.jscriptid]=(action,jscript)

                self.log("Job started:%s script: %s %s/%s"%(job.id, jscript.id,jscript.organization,jscript.name))
                try:
                    result=action(**job.args)
                    job.result=result
                    job.state="OK"
                    job.resultcode=0
                except Exception,e:                    
                    agentid=j.application.getAgentId()
                    msg="could not execute jscript:%s %s_%s on agent:%s\nError:%s"%(jscript.id,jscript.organization,jscript.name,agentid,e)
                    eco=j.errorconditionhandler.parsePythonErrorObject(e)
                    eco.errormessage = msg
                    eco.jid = job.id
                    eco.code=jscript.source
                    eco.category = "workers.executejob"
                    j.errorconditionhandler.processErrorConditionObject(eco)
                    # j.events.bug_warning(msg,category="worker.jscript.notexecute")
                    # self.loghandler.logECO(eco)
                    job.state="ERROR"
                    job.result=eco.errormessage
                self.notifyWorkCompleted(job)


    def notifyWorkCompleted(self,job):
        w=j.clients.redisworker
        job.timeStop=int(time.time())
        
        if job.state[0:2]<>"OK":
            self.log("result:%s"%job.result)

        if job.jscriptid>10000:
            # q=j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:return:%s"%jobid)
            w.redis.rpush("workers:return:%s"%job.id,time.time())
            self.redis.hset("workers:jobs",job.id, ujson.dumps(job.__dict__))
        else:
            #jumpscripts coming from AC
            if job.state<>"OK":
                try:
                    self.acclient.notifyWorkCompleted(job.__dict__)
                except Exception,e:
                    j.events.opserror("could not report job in error to agentcontroller", category='workers.errorreporting', e=e)
                    return
                #lets keep the errors
                # self.redis.hdel("workers:jobs",job.id)
            else:
                if job.log:
                    try:
                        self.acclient.notifyWorkCompleted(job.__dict__)
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

    opts = parser.parse_args()

    j.logger.consoleloglevel = 2
    j.logger.maxlevel=7

    worker=Worker(opts.addr, opts.port, opts.queuename)
    worker.run()

