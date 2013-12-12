from JumpScale import j

class system_infomgr_osis(j.code.classGetBase()):
    """
    this is an example actor
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.dbfs=j.db.keyvaluestore.getFileSystemStore(namespace="infomgr", baseDir=None,serializers=[j.db.serializers.getSerializerType('j')])
        self.db=self.dbfs
    

        pass

    def model_history_create(self, guid, month_5min, year_hour, **kwargs):
        """
        Create a new model
        param:guid is unique name (in dot notation)
        param:month_5min dict of measurements per 5 min, keep 31 days +1 h : 8929 items in dict
        param:year_hour dict of measurements per hour (per hour keep [nritems,total,min,max]), keep 12 months +1 day: 8761 items in dict
        result json 
        
        """
        
        history = self.models.history.new()
        history.guid = guid
        history.month_5min = month_5min
        history.year_hour = year_hour
        
        return self.models.history.set(history)
                
    

    def model_history_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.history.datatables() #@todo
                    
    

    def model_history_delete(self, id, guid='', **kwargs):
        """
        remove the model history with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.history.delete(guid=guid, id=id)
                    
    

    def model_history_find(self, query='', **kwargs):
        """
        query to model history
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.history.find(query)            
                    
    

    def model_history_get(self, id, guid='', **kwargs):
        """
        get model history with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.history.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_history_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.history.list()            
                    
    

    def model_history_new(self, **kwargs):
        """
        Create a new modelobjecthistory instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.history.new()
                    
    

    def model_history_set(self, data='', **kwargs):
        """
        Saves model history instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.history.set(data)            
                    
    

    def model_infotable_create(self, guid, infotable, **kwargs):
        """
        Create a new model
        param:guid is only one object with guid "infotable"
        param:infotable key ids used in system (dotnotation always in lcase)
        result json 
        
        """
        
        infotable = self.models.infotable.new()
        infotable.guid = guid
        infotable.infotable = infotable
        
        return self.models.infotable.set(infotable)
                
    

    def model_infotable_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.infotable.datatables() #@todo
                    
    

    def model_infotable_delete(self, id, guid='', **kwargs):
        """
        remove the model infotable with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.infotable.delete(guid=guid, id=id)
                    
    

    def model_infotable_find(self, query='', **kwargs):
        """
        query to model infotable
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.infotable.find(query)            
                    
    

    def model_infotable_get(self, id, guid='', **kwargs):
        """
        get model infotable with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.infotable.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_infotable_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.infotable.list()            
                    
    

    def model_infotable_new(self, **kwargs):
        """
        Create a new modelobjectinfotable instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.infotable.new()
                    
    

    def model_infotable_set(self, data='', **kwargs):
        """
        Saves model infotable instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.infotable.set(data)            
                    
    
