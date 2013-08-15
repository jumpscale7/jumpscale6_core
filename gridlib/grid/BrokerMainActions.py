from OpenWizzy import o

ZDaemonCMDS=o.core.zdaemon.getZDaemonCMDS()  #get base class which needs to be used as basis for commands

class BrokerMainActions(ZDaemonCMDS):

    def __init__(self, broker):
        

        self.broker = broker
        self.daemon=self.broker
        self.methods = {}
        self.applicationtypes={}

    def getactivejobs(self):
        return self.broker.activeJobs

    def ping(self):
        return "pong"

    def registerNode(self,obj):
        obj["gid"]=o.core.grid.id
        print '#####registernode'
        print obj
        print '#################'
        guid,new,changed=self.broker.osis_node.set(obj)  #@todo urgent new & changed does not return well (P1) 
            
        gid,id=guid.split("_")

        return id,self.broker.id

    def registerProcess(self,obj):
        obj["gid"]=o.core.grid.id
        print '#####registerprocess'
        print obj
        print '#################'
        guid,new,changed=self.broker.osis_process.set(obj) 
        gid,bid,id=guid.split("_")
        return id

    def registerApplication(self,name,description="",pid=0):
        zappl=o.core.grid.zobjects.getZApplicationObject(name=name,description=description)
        zappl.bid=self.broker.id
        print '#####appl'
        print zappl
        print '#################'

        key=zappl.getUniqueKey()
        if not self.applicationtypes.has_key(key):
            guid,new,changed=self.broker.osis_application.set(zappl.__dict__)
                
            gid,bid,id=guid.split("_")
            zappl.id=id
            zappl.getSetGuid()
            self.applicationtypes[key]=zappl
        else:
            zappl=self.applicationtypes[key]
        return zappl.id

    def registerAction(self, action):
        guid,new,changed=self.broker.osis_action.set(action)
        gid,bid,id=guid.split("_")
        self.broker.actions[int(id)]=action
        return id

    def getAction(self, actionid):        
        if not self.broker.actions.has_key(actionid):
            o.errorconditionhandler.raiseBug(message="could not find action with id %s"%actionid,category="broker.actions")
        return self.broker.actions[actionid]
        
    def registerWorker(self, obj,roles,instance,identity):
        workerprocess=o.core.grid.zobjects.getZProcessObject(ddict=obj)        
        self.broker.workers[identity] = [instance,roles]

        for role in roles:
            role=role.strip().lower()
            self.broker.registerRole4NewWorker(identity,role)

        o.logger.log("REGISTER WORKER:%s"%identity, level=3, category="broker.config")

        return True
