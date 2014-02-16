#!/usr/bin/env python

import sys
import time
import ujson
import psutil

from JumpScale.baselib import cmdutils
from JumpScale import j

j.application.start("jumpscale:worker")
j.application.initGrid()

# Preload libraries
j.system.platform.psutil=psutil
import JumpScale.baselib.graphite
import JumpScale.lib.diskmanager
import JumpScale.baselib.stataggregator
import JumpScale.grid.agentcontroller
import JumpScale.baselib.redis


class Worker(object):

    def __init__(self, redisaddr, redisport, queuename):
        self.client = j.clients.agentcontroller.get()
        self.actions={}

        self.redis = j.clients.redis.getGeventRedisClient(redisaddr, redisport)

        #@todo check if queue exists if not raise error
        self.queue=j.clients.redis.getRedisQueue(opts.addr, opts.port, "workers:work:%s" % queuename)

    def run(self):
        print "STARTED"
        while True:
            # jobid=self.queue.get()
            # data=self.redis.hget("workerjobs",jobid)
            try:
                # print "check if work", comes from redis
                jobid=self.queue.get()
                if jobid:
                    data=self.redis.hget("workerjobs",jobid)
                    if data:
                        job=ujson.loads(data)
                    else:
                        raise RuntimeError("cannot find job with id:%s"%jobid)
                else:
                    job=None
            except Exception,e:
                j.events.opserror("Could not get work from redis, is redis running?","workers.getwork",e)
                time.sleep(1)
                continue

            if job:
                organization=job["category"]
                name=job["cmd"]
                kwargs=job["args"]
                jid = job["id"]
                jscriptid = "%s_%s" % (organization, name)
                j.application.jid=jid
                #eval action code, if not ok send error back, cache the evalled action
                if self.actions.has_key(jscriptid):
                    action,jscript=self.actions[jscriptid]
                else:
                    # print "CACHEMISS"
                    jscript=ujson.loads(self.redis.hget("jumpscripts:%s"%(organization),name))
                    try:
                        self.log("Load script:%s %s"%(jscript["organization"],jscript["name"]))
                        exec(jscript["source"])
                        self.actions[jscriptid]=(action,jscript)
                        #result is method action
                    except Exception,e:
                        msg="could not compile jscript: %s_%s on agent:%s.\nCode was:\n%s\nError:%s"%(jscript["organization"],jscript["name"],j.application.getWhoAmiStr(),\
                            jscript["source"],e)

                        eco=j.errorconditionhandler.parsePythonErrorObject(e)
                        eco.errormessage = msg
                        eco.jid = jid
                        eco.category = 'agent_exec'
                        # self.loghandler.logECO(eco)
                        self.notifyWorkCompleted(jid,result={},eco=eco.__dict__)
                        continue

                eco=None
                self.log("Job started: %s %s"%(jscript["organization"],jscript["name"]))
                try:
                    result=action(**kwargs)
                except Exception,e:
                    msg="could not execute jscript: %s_%s on agent:%s.\nCode was:\n%s\nError:%s"%(jscript["organization"],jscript["name"],j.application.getWhoAmiStr(),\
                        jscript["source"],e)
                    eco=j.errorconditionhandler.parsePythonErrorObject(e)
                    eco.errormessage = msg
                    eco.jid = jid
                    eco.category = "workers.executejob"
                    # self.loghandler.logECO(eco)
                    self.notifyWorkCompleted(jid, {},eco.__dict__)
                    continue

                self.log("result:%s"%result)
                self.notifyWorkCompleted(jid, result,{})


    def notifyWorkCompleted(self,jid, result,eco):
        try:
            eco = eco.copy()
            eco.pop('tb', None)
            result=self.client.notifyWorkCompleted(jid, result=result,eco=eco)

        except Exception,e:
            eco = j.errorconditionhandler.lastEco
            j.errorconditionhandler.lastEco = None
            # self.loghandler.logECO(eco)

            print "******************* SERIOUS BUG **************"
            print "COULD NOT EXECUTE JOB, COULD NOT PROCESS RESULT OF WORK."
            try:
                print "ERROR WAS:%s"%eco, e
            except:
                print "COULD NOT EVEN PRINT THE ERRORCONDITION OBJECT"
            print "******************* SERIOUS BUG **************"


    def log(self, message, category='',level=5):
        #queue saving logs        
        j.logger.log(message,category=category,level=level)
        print message


if __name__ == '__main__':
    parser = cmdutils.ArgumentParser()
    parser.add_argument("-wn", '--workername', help='Worker name')
    parser.add_argument("-qn", '--queuename', help='Queue name', required=True)
    parser.add_argument("-pw", '--auth', help='Authentication of redis')
    parser.add_argument("-a", '--addr', help='Address of redis', required=True)
    parser.add_argument("-p", '--port', help='Port of redis', required=True)

    opts = parser.parse_args()

    j.logger.consoleloglevel = 2
    j.logger.maxlevel=7

    worker=Worker()
    worker.run()

