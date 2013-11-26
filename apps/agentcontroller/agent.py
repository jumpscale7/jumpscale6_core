from JumpScale import j

import time

import JumpScale.grid.geventws

import Queue

j.application.start("agent")

j.logger.consoleloglevel = 2

class Agent():

    def __init__(self):

        self.similarProcessPIDs=[process.pid for process in j.system.process.getSimularProcesses()]
        
        id=j.application.getWhoAmiStr()

        self.client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="user1", passwd="1234", \
            category="agent",id=id)


        self.agentid="%s_%s_%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid,j.application.whoAmI.pid)
        

        print "agent: %s"%self.agentid

        self.actions={}

        self.serverurl=self.client._client.transport.url

        self.register()

        self.client.schedule(self.flushLogs)

        self.queue = Queue.Queue()

    def register(self):
        ok=False
        while ok==False:
            try:
                self.client.register(similarProcessPIDs=self.similarProcessPIDs)
                ok=True
            except Exception,e:                
                print "retry registration to %s"%self.serverurl
                time.sleep(2)

    def start(self):
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
                # print "HAVEWORK"
                jscriptid,args=havework
                
                #eval action code, if not ok send error back, cache the evalled action
                if self.actions.has_key(jscriptid):
                    action,jscript=self.actions[jscriptid]
                else:
                    print "CACHEMISS"
                    jscript=self.client.getJumpscriptFromKey(jscriptid)
                    try:
                        self.queueLogs('Job started')
                        exec(jscript["source"])
                        self.actions[jscriptid]=(action,jscript)
                        #result is method action
                    except Exception,e:
                        msg="could not compile jscript: %s_%s on agent:%s.\nCode was:\n%s\nError:%s"%(jscript["organization"],jscript["name"],j.application.getWhoAmiStr(),\
                            jscript["source"],e)
                        eco=j.errorconditionhandler.getErrorConditionObject(msg=msg)
                        self.queueLogs(msg)
                        self.client.notifyWorkCompleted(result=None,eco=eco.__dict__)
                    
                eco=None
                try:
                    result=action(**args)
                except Exception,e:
                    msg="could not execute jscript: %s_%s on agent:%s.\nCode was:\n%s\nError:%s"%(jscript["organization"],jscript["name"],j.application.getWhoAmiStr(),\
                        jscript["source"],e)
                    eco=j.errorconditionhandler.getErrorConditionObject(msg=msg)
                    self.queueLogs(msg)
                    self.client.notifyWorkCompleted(result=None,eco=eco.__dict__)
                    continue
                
                print "notify work completed"
                self.client.notifyWorkCompleted(result=result,eco=None)

    def queueLogs(self, message, jid=0):
        #queue saving logs
        log = {'message': message, 'category': 'agent', 'jid':jid, 'parentjid': self.agentid}
        self.queue.put(log)

    def flushLogs(self):
        logs = []
        for i in range(0, self.queue.qsize()):
            logs.append(self.queue.get(block=False))
        return logs

agent=Agent()
agent.start()
