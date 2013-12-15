from JumpScale import j

class system_filemanager(j.code.classGetBase()):
    """
    manipulate our virtual filesystem
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="filemanager"
        self.appname="system"
        #system_filemanager_osis.__init__(self)
    

        pass

    def dirdelete(self, path, user, recursive=True, **kwargs):
        """
        param:path path of dir in unified namespace
        param:recursive if true will delete all files & dirs underneath default=True
        param:user user who modified the file
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method dirdelete")
    

    def filedelete(self, path, user, **kwargs):
        """
        param:path path of file in unified namespace
        param:user user who modified the file
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method filedelete")
    

    def filemod(self, path, user, **kwargs):
        """
        param:path path of new file in unified namespace
        param:user user who modified the file
        result str 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method filemod")
    

    def filenew(self, path, user, **kwargs):
        """
        param:path path of new file in unified namespace
        param:user user who modified the file
        result str 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method filenew")
    

    def getdirobject(self, id, **kwargs):
        """
        param:id unique id for dir object (is dirguid which is md5 path)
        result str 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getdirobject")
    

    def listdir(self, path, **kwargs):
        """
        param:path path of dir in unified namespace
        result list(str) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listdir")
    
