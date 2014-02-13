#!/usr/bin/env python
import sys
from redis import * 
# from rq import Queue, Connection, Worker

from JumpScale.baselib import cmdutils
from JumpScale import j
sys.path.insert(0,j.system.fs.joinPaths(j.dirs.varDir,"jumpscripts"))

import time
import ujson

j.application.start("jumpscale:worker")
j.application.initGrid()

parser = cmdutils.ArgumentParser()
parser.add_argument("-wn", '--workername', help='Worker name')
parser.add_argument("-qn", '--queuename', help='Queue name')
parser.add_argument("-pw", '--auth', help='Authentication of redis')
parser.add_argument("-a", '--addr', help='Address of redis')
parser.add_argument("-p", '--port', help='Port of redis')

opts = parser.parse_args()

# Preload libraries
import psutil
j.system.platform.psutil=psutil
import JumpScale.baselib.graphite
import JumpScale.lib.diskmanager
import JumpScale.baselib.stataggregator


# Provide queue names to listen to as arguments to this script,
# similar to rqworker

if opts.addr==None or opts.port==None:
    raise RuntimeError("Please provide addr & port")

import JumpScale.grid.geventws

j.logger.consoleloglevel = 2
j.logger.maxlevel=7

import ujson as json

import sys

REDISSERVER = '127.0.0.1'
REDISPORT = 7768

class Agent():

    def __init__(self):

        ipaddr=j.application.config.get("grid.master.ip")
        adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        adminuser = 'root'#j.application.config.get('system.superadmin.login')
        self.client = j.servers.geventws.getClient(ipaddr, 4444, org="myorg", user=adminuser, passwd=adminpasswd, category="agent",timeout=36000)

        self.actions={}
        # self.serverurl=self.client._client.transport.url

        self.redis = j.clients.redis.getGeventRedisClient(REDISSERVER, REDISPORT)

        #@todo check if queue exists if not raise error
        self.queue=j.clients.redis.getRedisQueue(REDISSERVER,REDISPORT,"workers:work:%s"%opts.queuename)

        self.run()

    def run(self):
        print "STARTED"
        while True:
            # jobid=self.queue.get()
            # data=self.redis.hget("workerjobs",jobid)
            try:
                # print "check if work", comes from redis
                jobid=self.queue.get()
                if jobid<>None:                
                    data=self.redis.hget("workerjobs",jobid)
                    if data<>None:
                        job=ujson.loads(data)
                    else:
                        raise RuntimeError("cannot find job with id:%s"%jobid)
                else:
                    job=None
                
            except Exception,e:
                j.events.opserror("Could not get work from redis, is redis running?","workers.getwork",e)
                # self.register()
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
                    # jscript=self.client.getJumpScript(organization, name)
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
                        eco.category = LOGS['agent']
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

                #if not j.basetype.dictionary.check(result):
                #    msg="agentcontroller: notifywork completed needs to have dicts as input for result & eco.\nScript started was: %s_%s.\n"%(jscript["organization"],jscript["name"])
                #   try:
                #        msg+="result was:%s\n"%result
                #    except:
                #        print "***ERROR***: could not print result"
                #    eco=j.errorconditionhandler.getErrorConditionObject(msg=msg)
                #    self.notifyWorkCompleted({},eco.__dict__)
                #    continue
                    
                
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



agent=Agent()
agent.run()

