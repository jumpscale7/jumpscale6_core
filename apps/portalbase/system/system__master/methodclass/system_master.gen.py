from JumpScale import j

class system_master(j.code.classGetBase()):
    """
    get dict of list of apps & actors
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="master"
        self.appname="system"
        #system_master_osis.__init__(self)
    

        pass

    def echo(self, input, **kwargs):
        """
        just a simple echo service
        param:input result will be same as this input
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method echo")
    

    def getAppsActors(self, model=1, **kwargs):
        """
        param:model if you want to also get model actors; otherwise 0 default=1
        result dict
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getAppsActors")
    

    def ping(self, **kwargs):
        """
        just a simple ping to the service (returns pong)
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method ping")
    

    def registerRedisInstance(self, ipaddr, port, secret, appname, actorname, **kwargs):
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
    
