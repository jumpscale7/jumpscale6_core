from JumpScale import j
from system_machinemanager_osis import system_machinemanager_osis


class system_machinemanager(system_machinemanager_osis):
    """
    manage the machines in a physical network
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="machinemanager"
        self.appname="system"
        system_machinemanager_osis.__init__(self)
    

        pass

    def executeAction(self, id, name, organization, arguments, **kwargs):
        """
        execute an action on a machine
        param:id unique id of machine
        param:name name of action
        param:organization name of action
        param:arguments arguments to the action (params)
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method executeAction")
    

    def initOverSSH(self, name, organization, ipaddr, passwd, login='root', **kwargs):
        """
        will ssh into the machin and install jumpscale & bootstrap the machine
        will also fetch the info from the machine & populate local portal
        param:name optional name of machine
        param:organization optional organization of machine
        param:ipaddr ip addr to start from
        param:login login to that machine default=root
        param:passwd passwd to that machine
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method initOverSSH")
    

    def initSelf(self, name, organization, **kwargs):
        """
        init local machine into db, give optional name & org info
        param:name name of action
        param:organization name of action
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method initSelf")
    
