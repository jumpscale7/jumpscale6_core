from JumpScale import j

import time

import JumpScale.grid.geventws

j.application.start("jumpscale:agent2")
j.application.initGrid()

j.logger.consoleloglevel = 2
j.logger.maxlevel=5

import ujson as json


import sys

class Agent():

    def __init__(self):

        self.agentid = j.application.getWhoAmiStr()

        ipaddr=j.application.config.get("grid.master.ip")
        adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        adminuser = 'root'#j.application.config.get('system.superadmin.login')
        self.client = j.servers.geventws.getClient(ipaddr, 4444, org="myorg", user=adminuser, passwd=adminpasswd, \
            category="agent",id=self.agentid,timeout=36000)

        print "agent: %s"%self.agentid

        self.serverurl=self.client._client.transport.url
        self.register()

    def register(self):
        print "REGISTERED"
        ok=False
        while ok==False:
            try:
                self.client.register()
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
                j.application.jid=jid
                
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
                        eco.category = LOGS['agent']
                        # self.loghandler.logECO(eco)
                        self.notifyWorkCompleted(result={},eco=eco.__dict__)
                        continue
                    
                eco=None
                self.log("Job started: %s %s"%(jscript["organization"],jscript["name"]))
                try:
                    LOGS['current'] = LOGS['job']
                    result=action(**args)
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
                    self.notifyWorkCompleted({},eco.__dict__)
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
                self.notifyWorkCompleted(result,{})


    def notifyWorkCompleted(self,result,eco):
        print self.client.listSessions()
        try:
            result=self.client.notifyWorkCompleted(result=result,eco=eco)
        except Exception,e:
            eco=j.errorconditionhandler.lastEco
            j.errorconditionhandler.lastEco=None
            # self.loghandler.logECO(eco)

            print "******************* SERIOUS BUG **************"
            print "COULD NOT EXECUTE JOB, COULD NOT PROCESS RESULT OF WORK."
            try:
                print "ERROR WAS:%s"%eco
            except:
                print "COULD NOT EVEN PRINT THE ERRORCONDITION OBJECT"
            print "******************* SERIOUS BUG **************"


    def log(self, message, category="",level=5):
        #queue saving logs        
        from IPython import embed
        print "DEBUG NOW ooo"
        embed()
        
        j.logger.log(message,category=category,level=level)
        print message



agent=Agent()
agent.start()


