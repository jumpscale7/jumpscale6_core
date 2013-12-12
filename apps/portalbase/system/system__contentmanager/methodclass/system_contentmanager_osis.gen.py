from JumpScale import j

class system_contentmanager_osis(j.code.classGetBase()):
    """
    this actor manages all content on the wiki
    can e.g. notify wiki/appserver of updates of content
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.db=self.dbmem
    

        pass

    def model_actor_create(self, application, actor, id, path, acl, **kwargs):
        """
        Create a new model
        param:application 
        param:actor 
        param:id is application__actor
        param:path 
        param:acl dict with key the group or username; and the value is a string
        result json 
        
        """
        
        actor = self.models.actor.new()
        actor.application = application
        actor.actor = actor
        actor.id = id
        actor.path = path
        actor.acl = acl
        
        return self.models.actor.set(actor)
                
    

    def model_actor_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.actor.datatables() #@todo
                    
    

    def model_actor_delete(self, id, guid='', **kwargs):
        """
        remove the model actor with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.actor.delete(guid=guid, id=id)
                    
    

    def model_actor_find(self, query='', **kwargs):
        """
        query to model actor
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.actor.find(query)            
                    
    

    def model_actor_get(self, id, guid='', **kwargs):
        """
        get model actor with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.actor.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_actor_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.actor.list()            
                    
    

    def model_actor_new(self, **kwargs):
        """
        Create a new modelobjectactor instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.actor.new()
                    
    

    def model_actor_set(self, data='', **kwargs):
        """
        Saves model actor instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.actor.set(data)            
                    
    

    def model_bucket_create(self, id, path, acl, **kwargs):
        """
        Create a new model
        param:id 
        param:path 
        param:acl dict with key the group or username; and the value is a string
        result json 
        
        """
        
        bucket = self.models.bucket.new()
        bucket.id = id
        bucket.path = path
        bucket.acl = acl
        
        return self.models.bucket.set(bucket)
                
    

    def model_bucket_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.bucket.datatables() #@todo
                    
    

    def model_bucket_delete(self, id, guid='', **kwargs):
        """
        remove the model bucket with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.bucket.delete(guid=guid, id=id)
                    
    

    def model_bucket_find(self, query='', **kwargs):
        """
        query to model bucket
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.bucket.find(query)            
                    
    

    def model_bucket_get(self, id, guid='', **kwargs):
        """
        get model bucket with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.bucket.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_bucket_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.bucket.list()            
                    
    

    def model_bucket_new(self, **kwargs):
        """
        Create a new modelobjectbucket instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.bucket.new()
                    
    

    def model_bucket_set(self, data='', **kwargs):
        """
        Saves model bucket instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.bucket.set(data)            
                    
    

    def model_space_create(self, id, path, acl, **kwargs):
        """
        Create a new model
        param:id is name of space
        param:path 
        param:acl dict with key the group or username; and the value is a string
        result json 
        
        """
        
        space = self.models.space.new()
        space.id = id
        space.path = path
        space.acl = acl
        
        return self.models.space.set(space)
                
    

    def model_space_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.space.datatables() #@todo
                    
    

    def model_space_delete(self, id, guid='', **kwargs):
        """
        remove the model space with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.space.delete(guid=guid, id=id)
                    
    

    def model_space_find(self, query='', **kwargs):
        """
        query to model space
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.space.find(query)            
                    
    

    def model_space_get(self, id, guid='', **kwargs):
        """
        get model space with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.space.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_space_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.space.list()            
                    
    

    def model_space_new(self, **kwargs):
        """
        Create a new modelobjectspace instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.space.new()
                    
    

    def model_space_set(self, data='', **kwargs):
        """
        Saves model space instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.space.set(data)            
                    
    
