from JumpScale import j

class system_usermanager(j.code.classGetBase()):
    """
    register a user (can be done by user itself, no existing key or login/passwd is needed)
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="usermanager"
        self.appname="system"
        #system_usermanager_osis.__init__(self)
    

        pass

    def authenticate(self, name, secret, **kwargs):
        """
        this needs to be used before rest api can be used
        param:name name
        param:secret md5 or passwd
        result str 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method authenticate")
    

    def getusergroups(self, user, **kwargs):
        """
        return list of groups in which user is member of
        param:user name of user
        result list(str) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getusergroups")
    

    def groupadduser(self, group, user, **kwargs):
        """
        add user to group
        param:group name of group
        param:user name of user
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method groupadduser")
    

    def groupcreate(self, name, groups, **kwargs):
        """
        create a group
        param:name name of group
        param:groups comma separated list of groups this group belongs to
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method groupcreate")
    

    def groupdeluser(self, group, user, **kwargs):
        """
        remove user from group
        param:group name of group
        param:user name of user
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method groupdeluser")
    

    def model_group_create(self, id, members, system=False, **kwargs):
        """
        Create a new model
        param:id is unique id =name
        param:members list members of group [username]
        param:system  default=False
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_group_create")
    

    def model_group_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_group_datatables")
    

    def model_group_delete(self, id, guid='', **kwargs):
        """
        remove the model group with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_group_delete")
    

    def model_group_find(self, query='', **kwargs):
        """
        query to model group
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_group_find")
    

    def model_group_get(self, id, guid='', **kwargs):
        """
        get model group with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_group_get")
    

    def model_group_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_group_list")
    

    def model_group_new(self, **kwargs):
        """
        Create a new modelobjectgroup instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_group_new")
    

    def model_group_set(self, data='', **kwargs):
        """
        Saves model group instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_group_set")
    

    def model_user_create(self, id, passwd, secret, emails, groups, **kwargs):
        """
        Create a new model
        param:id is unique id =name
        param:passwd 
        param:secret 
        param:emails list email addresses
        param:groups [groupname]
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_user_create")
    

    def model_user_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_user_datatables")
    

    def model_user_delete(self, id, guid='', **kwargs):
        """
        remove the model user with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_user_delete")
    

    def model_user_find(self, query='', **kwargs):
        """
        query to model user
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_user_find")
    

    def model_user_get(self, id, guid='', **kwargs):
        """
        get model user with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_user_get")
    

    def model_user_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_user_list")
    

    def model_user_new(self, **kwargs):
        """
        Create a new modelobjectuser instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_user_new")
    

    def model_user_set(self, data='', **kwargs):
        """
        Saves model user instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_user_set")
    

    def usercreate(self, name, passwd, key, groups, emails, config, userid=0, reference="''", remarks="''", **kwargs):
        """
        create a user
        param:name name of user
        param:passwd passwd
        param:key specific key can be empty
        param:groups comma separated list of groups this user belongs to
        param:emails comma separated list of email addresses
        param:userid optional user id; leave 0 when not used; when entered will update existing record default=0
        param:reference reference as used in other application using this API (optional) default=''
        param:remarks free to be used field by client default=''
        param:config free to be used field to store config information e.g. in json or xml format
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method usercreate")
    

    def userexists(self, name, **kwargs):
        """
        param:name name
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method userexists")
    

    def userexistsFromId(self, userid, **kwargs):
        """
        param:userid id
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method userexistsFromId")
    

    def userregister(self, name, passwd, emails, config, reference="''", remarks="''", **kwargs):
        """
        param:name name of user
        param:passwd chosen passwd (will be stored hashed in DB)
        param:emails comma separated list of email addresses
        param:reference reference as used in other application using this API (optional) default=''
        param:remarks free to be used field by client default=''
        param:config free to be used field to store config information e.g. in json or xml format
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method userregister")
    
