from JumpScale import j

class system_usermanager_osis(j.code.classGetBase()):
    """
    register a user (can be done by user itself, no existing key or login/passwd is needed)
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.dbfs=j.db.keyvaluestore.getFileSystemStore(namespace="usermanager", baseDir=None,serializers=[j.db.serializers.getSerializerType('j')])
        self.db=self.dbfs
    

        pass

    def model_group_create(self, id, members, system=False, **kwargs):
        """
        Create a new model
        param:id is unique id =name
        param:members list members of group [username]
        param:system  default=False
        result json 
        
        """
        
        group = self.models.group.new()
        group.id = id
        group.members = members
        group.system = system
        
        return self.models.group.set(group)
                
    

    def model_group_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.group.datatables() #@todo
                    
    

    def model_group_delete(self, id, guid='', **kwargs):
        """
        remove the model group with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.group.delete(guid=guid, id=id)
                    
    

    def model_group_find(self, query='', **kwargs):
        """
        query to model group
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.group.find(query)            
                    
    

    def model_group_get(self, id, guid='', **kwargs):
        """
        get model group with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.group.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_group_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.group.list()            
                    
    

    def model_group_new(self, **kwargs):
        """
        Create a new modelobjectgroup instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.group.new()
                    
    

    def model_group_set(self, data='', **kwargs):
        """
        Saves model group instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.group.set(data)            
                    
    

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
        
        user = self.models.user.new()
        user.id = id
        user.passwd = passwd
        user.secret = secret
        user.emails = emails
        user.groups = groups
        
        return self.models.user.set(user)
                
    

    def model_user_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.user.datatables() #@todo
                    
    

    def model_user_delete(self, id, guid='', **kwargs):
        """
        remove the model user with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.user.delete(guid=guid, id=id)
                    
    

    def model_user_find(self, query='', **kwargs):
        """
        query to model user
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.user.find(query)            
                    
    

    def model_user_get(self, id, guid='', **kwargs):
        """
        get model user with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.user.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_user_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.user.list()            
                    
    

    def model_user_new(self, **kwargs):
        """
        Create a new modelobjectuser instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.user.new()
                    
    

    def model_user_set(self, data='', **kwargs):
        """
        Saves model user instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.user.set(data)            
                    
    
