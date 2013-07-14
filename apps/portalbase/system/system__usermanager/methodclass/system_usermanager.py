from OpenWizzy import o
from system_usermanager_osis import system_usermanager_osis

class system_usermanager(system_usermanager_osis):
    """
    register a user (can be done by user itself, no existing key or login/passwd is needed)
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="usermanager"
        self.appname="system"
        system_usermanager_osis.__init__(self)

    def authenticate(self,name,secret,**args):
        """
        this needs to be used before rest api can be used
        param:name name
        param:secret md5 or passwd
        result str 
        
        """
        usermanager=o.apps.system.usermanager
        user=usermanager.extensions.usermanager.userGet(name, usecache=False)

        if user==None:
            return False
        if user.passwd.strip()==str(secret).strip():
            return True
        if o.tools.hash.md5_string(user.passwd.strip())==str(secret).strip():
            return True
        result=False
        return result
    

    def getusergroups(self,user,**args):
        """
        return list of groups in which user is member of
        param:user name of user
        result list(str) 
        
        """
        usermanager=o.apps.system.usermanager
        user=usermanager.extensions.usermanager.userGet(user)

        if user==None:
            #did not find user
            result=[]
        else:
            #print "usergroups:%s" % user.groups
            result=user.groups

        return result
    

    def groupadduser(self,group,user,**args):
        """
        add user to group
        param:group name of group
        param:user name of user
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method groupadduser")
    

    def groupcreate(self,name,groups,**args):
        """
        create a group
        param:name name of group
        param:groups comma separated list of groups this group belongs to
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method groupcreate")
    

    def groupdeluser(self,group,user,**args):
        """
        remove user from group
        param:group name of group
        param:user name of user
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method groupdeluser")
    

    def usercreate(self,name,passwd,key,groups,emails,userid,reference,remarks,config,**args):
        """
        create a user
        param:name name of user
        param:passwd passwd
        param:key specific key can be empty
        param:groups comma separated list of groups this user belongs to
        param:emails comma separated list of email addresses
        param:userid optional user id; leave 0 when not used; when entered will update existing record
        param:reference reference as used in other application using this API (optional)
        param:remarks free to be used field by client
        param:config free to be used field to store config information e.g. in json or xml format
        result bool 
        
        """
        groups=groups.split(",")
        emails=emails.split(",")
        if userid==0:
            userid=None
        else:
            userid=userid
        result=o.apps.system.usermanager.extensions.usermanager.usercreate(name=name,passwd=passwd, groups=groups, emails=emails,userid=userid)
        return result
    

    def userexists(self,name,**args):
        """
        param:name name
        result bool 
        
        """
        usermanager=o.apps.system.usermanager
        user=usermanager.extensions.usermanager.userGet(name)
        if user==None:
            return False
        else:
            return True

    def userexistsFromId(self,userid,**args):
        """
        param:userid id
        result bool 
        
        """
        result= not (o.apps.system.usermanager_model_user.get(userid,"")==False)
        return result
    

    def userregister(self,name,passwd,emails,reference,remarks,config,**args):
        """
        param:name name of user
        param:passwd chosen passwd (will be stored hashed in DB)
        param:emails comma separated list of email addresses
        param:reference reference as used in other application using this API (optional)
        param:remarks free to be used field by client
        param:config free to be used field to store config information e.g. in json or xml format
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method userregister")
    
