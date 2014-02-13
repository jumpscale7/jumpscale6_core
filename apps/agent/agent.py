from JumpScale import j
import gevent
from gevent import Greenlet

import time

import JumpScale.grid.geventws

import Queue

j.application.start("jumpscale:agent")
j.application.initGrid()

j.logger.consoleloglevel = 2
j.logger.maxlevel=7

import ujson as json

LOGS = {'current':'agent',
        'agent': 'agent',
        'job': 'agent_job' }

class LogHandler(Greenlet):

    def __init__(self,agent):
        Greenlet.__init__(self)
        self.enabled = True
        self.agent=agent
        self.queue = Queue.Queue()
        self.jid=j.application.jid

    def log(self,logitem):
        logitem.jid=self.jid
        if not logitem.category:
            logitem.category = LOGS['current']
        self.queue.put(logitem.__dict__)
        print logitem

    def logECO(self, eco):
        eco.jid = self.jid
        if not isinstance(eco.type, int):
            eco.type = eco.type.level
        self.agent.client.escalateError(eco)

    def flushLogs(self):
        logs = []
        while not self.queue.empty():
            logs.append(self.queue.get(block=False))
        if logs:
            self.agent.client.log(logs)

    def _run(self, interval=5):
        while True:
            gevent.sleep(interval)
            self.flushLogs()

    def close(self):
        self.flushLogs()

import sys

class Agent(Greenlet):

    def __init__(self):
        Greenlet.__init__(self)
        self.loghandler=LogHandler(self)

        j.logger.logTargets=[]
        j.logger.logTargetLogForwarder=False

        ipaddr=j.application.config.get("grid.master.ip")
        adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        adminuser = 'root'#j.application.config.get('system.superadmin.login')
        self.client = j.servers.geventws.getClient(ipaddr, 4444, org="myorg", user=adminuser, passwd=adminpasswd, category="agent",timeout=36000)

        j.logger.logTargetAdd(self.loghandler)
        self.loghandler.start()        
        # setup logger
        if not j.logger.logTargetLogForwarder:
            j.logger.logTargetLogForwarder = self.loghandler

        sys.excepthook=self.exceptHook

        self.actions={}
        self.serverurl=self.client._client.transport.url
        self.register()

    def exceptHook(self,type, value, traceback):
        print "******************* SERIOUS BUG **************"
        print "COULD NOT EXECUTE JOB"
        eco=j.errorconditionhandler.processPythonExceptionObject(value)
        eco.getBacktraceDetailed(traceback)
        try:
            j.errorconditionhandler.processErrorConditionObject(eco)
        except:
            print "COULD NOT PROCESS ERRORCONDITION OBJECT"
            try:
                print eco
            except:
                print "COULD NOT EVEN PRINT THE ERRORCONDITION OBJECT"
        print "******************* SERIOUS BUG **************"   
        self.register()
        self._run()

    def register(self):
        print "REGISTER:",
        ok=False
        while ok==False:
            try:
                self.client.register()
                ok=True
            except Exception,e:
                print e
                print "retry registration"
                gevent.sleep(2)
        print "OK"

    def _run(self):
        print "STARTED"
        while True:

            ok=False
            while ok==False:
                try:
                    # print "check if work"
                    job=self.client.getWork()
                    ok=True
                except Exception,e:
                    self.register()
                    continue

            if not havework:
                print 'no work here'
                
            if job and ok:
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
                    jscript=self.client.getJumpScript(organization, name)
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
                        self.notifyWorkCompleted(result={},eco=eco.__dict__)
                        continue
                    
                eco=None
                self.log("Job started: %s %s"%(jscript["organization"],jscript["name"]))
                try:
                    LOGS['current'] = LOGS['job']
                    result=action(**kwargs)
                    LOGS['current'] = LOGS['agent']
                except Exception,e:
                    LOGS['current'] = LOGS['agent']
                    msg="could not execute jscript: %s_%s on agent:%s.\nCode was:\n%s\nError:%s"%(jscript["organization"],jscript["name"],j.application.getWhoAmiStr(),\
                        jscript["source"],e)
                    eco=j.errorconditionhandler.parsePythonErrorObject(e)
                    eco.errormessage = msg
                    eco.jid = jid
                    eco.category = LOGS['agent']
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


    def log(self, message, category=LOGS['agent'],level=5):
        #queue saving logs        
        j.logger.log(message,category=category,level=level)
        print message



agent=Agent()
agent.start()
agent.join()

