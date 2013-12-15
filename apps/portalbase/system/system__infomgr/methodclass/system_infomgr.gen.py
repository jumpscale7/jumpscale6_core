from JumpScale import j

class system_infomgr(j.code.classGetBase()):
    """
    this is an example actor
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="infomgr"
        self.appname="system"
        #system_infomgr_osis.__init__(self)
    

        pass

    def addInfo(self, info, **kwargs):
        """
        can be multi line
        param:info dotnotation of info e.g. 'water.white.level.sb 10'  (as used in graphite)
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addInfo")
    

    def getInfo1h(self, id, start=0, stop=0, **kwargs):
        """
        return raw info (resolution is 1h)
        param:id id in dot noation e.g. 'water.white.level.sb' (can be multiple use comma as separation)
        param:start epoch; 0 means all default=0
        param:stop epoch; 0 means all default=0
        result list(list) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getInfo1h")
    

    def getInfo1hFromTo(self, id, start, stop, **kwargs):
        """
        will not return more than 12 months of info, resolution = 1h
        param:id id in dot noation e.g. 'water.white.level.sb'
        param:start epoch
        param:stop epoch
        result dict() 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getInfo1hFromTo")
    

    def getInfo5Min(self, id, start=0, stop=0, **kwargs):
        """
        return raw info (resolution is 5min)
        param:id id in dot noation e.g. 'water.white.level.sb' (can be multiple use comma as separation)
        param:start epoch; 0 means all default=0
        param:stop epoch; 0 means all default=0
        result list(list) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getInfo5Min")
    

    def getInfo5MinFromTo(self, id, start, stop, **kwargs):
        """
        will not return more than 1 month of info
        param:id id in dot noation e.g. 'water.white.level.sb'
        param:start epoch
        param:stop epoch
        result dict() 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getInfo5MinFromTo")
    

    def getInfoWithHeaders(self, id, start, stop, maxvalues=360, **kwargs):
        """
        param:id id in dot noation e.g. 'water.white.level.sb'  (can be multiple use comma as separation)
        param:start epoch
        param:stop epoch
        param:maxvalues nr of values you want to return default=360
        result list(list) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getInfoWithHeaders")
    

    def model_history_create(self, guid, month_5min, year_hour, **kwargs):
        """
        Create a new model
        param:guid is unique name (in dot notation)
        param:month_5min dict of measurements per 5 min, keep 31 days +1 h : 8929 items in dict
        param:year_hour dict of measurements per hour (per hour keep [nritems,total,min,max]), keep 12 months +1 day: 8761 items in dict
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_history_create")
    

    def model_history_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_history_datatables")
    

    def model_history_delete(self, id, guid='', **kwargs):
        """
        remove the model history with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_history_delete")
    

    def model_history_find(self, query='', **kwargs):
        """
        query to model history
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_history_find")
    

    def model_history_get(self, id, guid='', **kwargs):
        """
        get model history with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_history_get")
    

    def model_history_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_history_list")
    

    def model_history_new(self, **kwargs):
        """
        Create a new modelobjecthistory instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_history_new")
    

    def model_history_set(self, data='', **kwargs):
        """
        Saves model history instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_history_set")
    

    def model_infotable_create(self, guid, infotable, **kwargs):
        """
        Create a new model
        param:guid is only one object with guid "infotable"
        param:infotable key ids used in system (dotnotation always in lcase)
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_infotable_create")
    

    def model_infotable_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_infotable_datatables")
    

    def model_infotable_delete(self, id, guid='', **kwargs):
        """
        remove the model infotable with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_infotable_delete")
    

    def model_infotable_find(self, query='', **kwargs):
        """
        query to model infotable
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_infotable_find")
    

    def model_infotable_get(self, id, guid='', **kwargs):
        """
        get model infotable with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_infotable_get")
    

    def model_infotable_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_infotable_list")
    

    def model_infotable_new(self, **kwargs):
        """
        Create a new modelobjectinfotable instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_infotable_new")
    

    def model_infotable_set(self, data='', **kwargs):
        """
        Saves model infotable instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_infotable_set")
    

    def reset(self, **kwargs):
        """
        reset all stats
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method reset")
    
