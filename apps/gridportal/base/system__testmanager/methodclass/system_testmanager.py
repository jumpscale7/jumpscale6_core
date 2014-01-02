from JumpScale import j

class system_testmanager(j.code.classGetBase()):
    """
    expose test results
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="testmanager"
        self.appname="system"
        #system_testmanager_osis.__init__(self)
    

        pass

    def getTests(self, nid, domain, **kwargs):
        """
        param:nid id of node
        param:domain optional domain name for jpackage
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getTests")
    
