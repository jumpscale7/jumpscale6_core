from JumpScale import j

import time

import JumpScale.grid.geventws

import Queue

import threading

j.application.start("agent")

j.logger.consoleloglevel = 2
j.logger.maxlevel=7

import ujson as json

LOGCATEGORY = 'agent_exec'

class LogHandler():

    def __init__(self,agent):
        self.enabled = True
        self.agent=agent
        self.queue = Queue.Queue()
        self.jid=""
        self._running = False

    def log(self,logitem):
        logitem.jid=self.jid
        if not logitem.category:
            logitem.category = LOGCATEGORY
        self.queue.put(logitem.__dict__)
        print logitem

    def logECO(self, eco):
        eco.jid = self.jid
        if not isinstance(eco.type, int):
            eco.type = eco.type.level
        self.agent.client.escalateError(eco.__dict__)

    def flushLogs(self):
        logs = []
        while not self.queue.empty():
            logs.append(self.queue.get(block=False))
        if logs:
            self.agent.client.log(logs)

    def start(self, interval=5):
        self._running = True
        class MyFlush(threading.Thread):
            def run(s):
                while self._running:
                    time.sleep(interval)
                    self.flushLogs()
        print "log thread started, will flush each %s sec"%interval
        self._t = MyFlush()
        self._t.setDaemon(True)
        self._t.start()  

    def stop(self):
        self._running = False

    def __exit__(self):
        self._running = False

    def close(self):
        self.stop()

import sys

class Agent():

    def __init__(self):

        self.loghandler=LogHandler(self)

        

        j.logger.logTargets=[]
        j.logger.logTargetLogForwarder=False

        self.similarProcessPIDs=[process.pid for process in j.system.process.getSimularProcesses()]
        
        id=j.application.getWhoAmiStr()

        self.client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="user1", passwd="1234", \
            category="agent",id=id,timeout=36000)

        self.agentid="%s_%s_%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid,j.application.whoAmI.pid)

        j.logger.logTargetAdd(self.loghandler)
        self.loghandler.start()        
        # setup logger
        if not j.logger.logTargetLogForwarder:
            j.logger.logTargetLogForwarder = self.loghandler

        print "agent: %s"%self.agentid

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
        self.start()     

    def register(self):
        print "REGISTERED"
        ok=False
        while ok==False:
            try:
                self.client.register(similarProcessPIDs=self.similarProcessPIDs)
                ok=True
            except Exception,e:
                print e
                print "retry registration"
                time.sleep(2)

    def start(self):
        print "STARTED"
        while True:

            ok=False
            while ok==False:
                try:
                    # print "check if work"
                    havework=self.client.getWork()
                    ok=True
                except Exception,e:
                    self.register()
                    continue
                
            if havework<>None and ok:
                jscriptid,args,jid=havework
                args=json.loads(args)
                self.loghandler.jid=jid
                
                #eval action code, if not ok send error back, cache the evalled action
                if self.actions.has_key(jscriptid):
                    action,jscript=self.actions[jscriptid]
                else:
                    # print "CACHEMISS"
                    jscript=self.client.getJumpscriptFromKey(jscriptid)
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
                        eco.category = LOGCATEGORY
                        self.notifyWorkCompleted(result={},eco=eco.__dict__)
                        continue
                    
                eco=None
                self.log("Job started: %s %s"%(jscript["organization"],jscript["name"]))
                try:
                    result=action(**args)
                except Exception,e:
                    msg="could not execute jscript: %s_%s on agent:%s.\nCode was:\n%s\nError:%s"%(jscript["organization"],jscript["name"],j.application.getWhoAmiStr(),\
                        jscript["source"],e)
                    eco=j.errorconditionhandler.parsePythonErrorObject(e)
                    eco.errormessage = msg
                    eco.jid = jid
                    eco.category = LOGCATEGORY
                    self.notifyWorkCompleted({},eco.__dict__)
                    continue

                if not j.basetype.dictionary.check(result):
                    msg="agentcontroller: notifywork completed needs to have dicts as input for result & eco.\nScript started was: %s_%s.\n"%(jscript["organization"],jscript["name"])
                    try:
                        msg+="result was:%s\n"%result
                    except:
                        print "***ERROR***: could not print result"
                    eco=j.errorconditionhandler.getErrorConditionObject(msg=msg)
                    self.notifyWorkCompleted({},eco.__dict__)
                    continue
                    
                
                self.log("result:%s"%result)
                self.notifyWorkCompleted(result,{})


    def notifyWorkCompleted(self,result,eco):
        try:
            result=self.client.notifyWorkCompleted(result=result,eco=eco,transporttimeout=5)
        except Exception,e:
            eco=j.errorconditionhandler.lastEco
            j.errorconditionhandler.lastEco=None

            print "******************* SERIOUS BUG **************"
            print "COULD NOT EXECUTE JOB, COULD NOT PROCESS RESULT OF WORK."
            try:
                print "ERROR WAS:%s"%eco
            except:
                print "COULD NOT EVEN PRINT THE ERRORCONDITION OBJECT"
            print "******************* SERIOUS BUG **************"


    def log(self, message, category=LOGCATEGORY,level=5):
        #queue saving logs        
        j.logger.log(message,category=category,level=level)
        print message



agent=Agent()
agent.start()
