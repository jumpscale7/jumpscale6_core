from pylabs import q
from system_master_osis import *

class system_master(system_master_osis):
    """
    get dict of list of apps & actors
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="master"
        self.appname="system"
        system_master_osis.__init__(self)
    
    def echo(self,input,**args):
        """
        just a simple echo service
        param:input result will be same as this input
        result str 
        
        """
        return input
    

    def getAppsActors(self,model,**args):
        """
        param:model if you want to also get model actors; otherwise 0
        result dict 
        
        """
        if int(model)==1:
            result= q.core.specparser.app_actornames
        else:
            result={}
            for app in q.core.specparser.app_actornames.keys():
                result[app]=[]
                actors=q.core.specparser.app_actornames[app]
                for actor in actors:
                    if actor.find("_model_")==-1:
                        result[app].append(actor)

        return result
    

    def ping(self,**args):
        """
        just a simple ping to the service        
        """
        return "pong"
    

    def registerRedisInstance(self,ipaddr,port,secret,appname,actorname,**args):
        """
        get dict of list of apps & actors
        param:ipaddr ipaddr of instance
        param:port port
        param:secret secret
        param:appname appname
        param:actorname actorname
        result dict 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method registerRedisInstance")
    
