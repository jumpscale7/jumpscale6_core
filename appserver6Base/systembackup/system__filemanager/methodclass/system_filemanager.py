from pylabs import q
from system_filemanager_osis import *

class system_filemanager(system_filemanager_osis):
    """
    manipulate our virtual filesystem
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="filemanager"
        self.appname="system"
        system_filemanager_osis.__init__(self)
    

        pass

    def dirdelete(self,path,recursive,user,**args):
        """
        param:path path of dir in unified namespace
        param:recursive if true will delete all files & dirs underneath
        param:user user who modified the file
        result bool 
        
        """
        args={}
        args["path"]=path
        args["recursive"]=recursive
        args["user"]=user
        return self._te["dirdelete"].execute4method(args,params={},actor=self)
    

    def filedelete(self,path,user,**args):
        """
        param:path path of file in unified namespace
        param:user user who modified the file
        result bool 
        
        """
        args={}
        args["path"]=path
        args["user"]=user
        return self._te["filedelete"].execute4method(args,params={},actor=self)
    

    def filemod(self,path,user,**args):
        """
        param:path path of new file in unified namespace
        param:user user who modified the file
        result str 
        
        """
        args={}
        args["path"]=path
        args["user"]=user
        return self._te["filemod"].execute4method(args,params={},actor=self)
    

    def filenew(self,path,user,**args):
        """
        param:path path of new file in unified namespace
        param:user user who modified the file
        result str 
        
        """
        args={}
        args["path"]=path
        args["user"]=user
        return self._te["filenew"].execute4method(args,params={},actor=self)
    

    def getdirobject(self,id,**args):
        """
        param:id unique id for dir object (is dirguid which is md5 path)
        result str 
        
        """
        args={}
        args["id"]=id
        return self._te["getdirobject"].execute4method(args,params={},actor=self)
    

    def listdir(self,path,**args):
        """
        param:path path of dir in unified namespace
        result list(str) 
        
        """
        args={}
        args["path"]=path
        return self._te["listdir"].execute4method(args,params={},actor=self)
    
