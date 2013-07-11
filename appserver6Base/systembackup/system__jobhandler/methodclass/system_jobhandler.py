from pylabs import q
from system_jobhandler_osis import *

class system_jobhandler(system_jobhandler_osis):
    """
    execute a job
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="jobhandler"
        self.appname="system"
        system_jobhandler_osis.__init__(self)
    

        pass

    def execute(self,actormethod,defname,defcode,defargs,name,category,errordescr,recoverydescr,maxtime,defpath,defagentid,channel,location,user,wait,defmd5,**args):
        """
        param:actormethod $app.$actor.$method
        param:defname 
        param:defcode 
        param:defargs 
        param:name 
        param:category optional category of job e.g. system.fs.copyfiles (free to be chosen)
        param:errordescr 
        param:recoverydescr 
        param:maxtime is max time call should take in secs
        param:defpath 
        param:defagentid 
        param:channel channel
        param:location location
        param:user 
        param:wait wait till job finishes
        param:defmd5 
        result str 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method execute")
    
