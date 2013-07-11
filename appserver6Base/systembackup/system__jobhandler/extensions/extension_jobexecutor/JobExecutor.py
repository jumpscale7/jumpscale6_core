
from pylabs import q
from multiprocessing import Process, Queue

def worker(q):    
    q.put("test")

class JobExecutor():
    def __init__(self):
        self.inited=False
        self.jfunctions={}        
        self.jobdb=q.apps.system.jobhandler.models.job
        self.workerQueues={}
        self.workerProcesses={}

        for i in range(1):
            from pylabs.Shell import ipshellDebug,ipshell
            print "DEBUG NOW id"
            ipshell()
            
            self.workerQueues[i]=Queue()
            self.workerProcesses[i]=Process(target=worker, args=(self.workerQueues[i],))
            self.workerProcesses[i].start()

        from pylabs.Shell import ipshellDebug,ipshell
        print "DEBUG NOW kk"
        ipshell()
        
        
    def getJobObjFromArgs(self,actormethod="",\
            defname="",\
            defcode="",\
            defpath="",\
            defagentid="",\
            name="",\
            category="",\
            errordescr="",\
            recoverydescr="",\
            maxtime="",\
            channel="",\
            location="",\
            user="",\
            wait="",\
            defargs={},
            defmd5=""):
        
        job=self.jobdb.new()
        job.actormethod=str(actormethod)
        job.defname=str(defname)
        job.defcode=str(defcode)
        job.defpath=str(defpath)
        job.defagentid=str(defagentid)
        job.name=str(name)
        job.category=str(category)
        job.errordescr=str(errordescr)
        job.recoverydescr=str(recoverydescr)
        job.maxtime=int(maxtime)
        job.channel=str(channel)
        job.location=str(location)
        job.user=str(user)
        job.wait=wait
        job.defargs=str(defargs)
        job.defmd5=str(defmd5)
        return job

    def scheduleNowWait(self,jobobj):
        from pylabs.Shell import ipshellDebug,ipshell
        print "DEBUG NOW schedule"
        ipshell()
        


    def executeInProcess(self,jobobj):

        if self.jfunctions.has_key(jobobj.defmd5):
            jfunc=self.jfunctions[jobobj.defmd5]
        else:
            try:
                exec(jobobj.defcode)            
            except Exception,e:
                jobobj.state="error"
                jobobj.errordescr="Syntax error probably in def, check the code & try again. Could not import.Error was:\n%s"%e
                return jobobj


            self.jfunctions[jobobj.defmd5]=jfunc

        args=q.tools.json.decode(defargs)
        result=jfunc(**args)


        from pylabs.Shell import ipshellDebug,ipshell
        print "DEBUG NOW id"
        ipshell()
        
        

