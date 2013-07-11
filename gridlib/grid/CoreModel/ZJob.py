from OpenWizzy import o
from ZBase import *
import struct

class ZJob(ZBase):
    def __init__(self,ddict={},executorrole="",actionid=0,args={},jidmaster=0,jidparent=0,allworkers=True):
        if ddict<>{}:
            self.__dict__=ddict
        else:
            self.guid=""
            self.gid=o.core.grid.id
            self.bid=o.core.grid.bid #broker id
            self.aid=o.core.grid.aid #application id which is unique per broker, application type which asked for this job (is a type not a specific instance of an app)
            self.cpid=o.core.grid.processobject.id #client_pid refers to process which asked for this job (running the application) = unique per broker
            o.core.grid.processobject.lastJobId+=1
            self.jid=o.core.grid.processobject.lastJobId #id of job (increments per process)
            self.args=args
            self.actionid=actionid
            self.result={}
            self.ecid=0 #if of errorcondition (unique per broker & grid)
            self.state="init"
            self.allworkers=allworkers
            self.executorrole=executorrole
            self.childrenWaiting=[] #refers to jids
            self.childrenActive=[]#refers to jids
            self.childrenError=[]#refers to jids
            self.childrenDone=[]#refers to jids
            self.parent=jidparent#refers to jids
            self.master=jidmaster#refers to jids
            self.wpid=0 #worker_pid refers to process id of a worker = unique id for process which represents the worker (unique per broker)
            self.getSetGuid()

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.getContentKey()

    def getSetGuid(self):
        """
        gid=grid id
        bid=broker id
        aid=application id
        jid=jobid
        """
        self.gid=int(self.gid)
        self.bid=int(self.bid)
        self.aid=int(self.aid)

        self.guid="%s_%s_%s_%s"%(self.gid,self.bid,self.aid,self.jid)
        # self.sguid=struct.pack("<HHHL",self.gid,self.bid,self.aid,self.jid)
        return self.guid


    def getIDs(self):
        """
        return (gid,bid,aid,jid)
        gid=grid id
        bid=broker id
        aid=application id
        jid=jobid
        """
        return struct.unpack("<HHHL",self.sguid)

    def getGuidParts(self):
        return ["gid","bid","aid","jid"]

    def log(self,msg,category,level=7):
        from OpenWizzy.core.Shell import ipshellDebug,ipshell
        print "DEBUG NOW log zjob.py"
        ipshell()

    def setProgress(self,progress):
        """
        in int (0-100)
        """
        self.progress=progress
        self.log("progress:%s"%progress,"job.progress",9)            

    def getCategory(self):
        return "zjob"
    
    def getObjectType(self):
        return 2

    def getVersion(self):
        return 1

    def getMessage(self):
        #[$objecttype,$objectversion,guid,$object=data]
        return [2,1,self.sguid,self.__dict__]

