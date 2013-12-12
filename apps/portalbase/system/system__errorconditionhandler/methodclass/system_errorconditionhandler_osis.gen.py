from JumpScale import j

class system_errorconditionhandler_osis(j.code.classGetBase()):
    """
    errorcondition handling
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.dbfs=j.db.keyvaluestore.getFileSystemStore(namespace="errorconditionhandler", baseDir=None,serializers=[j.db.serializers.getSerializerType('j')])
        self.db=self.dbfs
    

        pass

    def model_errorcondition_create(self, guid, appname, actorname, description, descriptionpub, level, category, tags, inittime, lasttime, closetime, traceback, state=' state is "NEW', nrerrorconditions=1, **kwargs):
        """
        Create a new model
        param:guid is guid
        param:appname name for application which generated the error condition
        param:actorname name for actor which generated the error condition
        param:description description for private (developer) usage
        param:descriptionpub description as what can be read by endusers
        param:level 1:critical, 2:warning, 3:info
        param:category dot notation e.g. machine.start.failed
        param:tags pylabs tag string, can be used to put addtional info e.g. vmachine:2323
        param:state "ALERT" or "CLOSED" default= state is "NEW
        param:inittime first time there was an error condition linked to this alert
        param:lasttime last time there was an error condition linked to this alert
        param:closetime alert is closed, no longer active
        param:nrerrorconditions nr of times this error condition happened default=1
        param:traceback optional traceback info e.g. for bug
        result json 
        
        """
        
        errorcondition = self.models.errorcondition.new()
        errorcondition.guid = guid
        errorcondition.appname = appname
        errorcondition.actorname = actorname
        errorcondition.description = description
        errorcondition.descriptionpub = descriptionpub
        errorcondition.level = level
        errorcondition.category = category
        errorcondition.tags = tags
        errorcondition.state = state
        errorcondition.inittime = inittime
        errorcondition.lasttime = lasttime
        errorcondition.closetime = closetime
        errorcondition.nrerrorconditions = nrerrorconditions
        errorcondition.traceback = traceback
        
        return self.models.errorcondition.set(errorcondition)
                
    

    def model_errorcondition_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.errorcondition.datatables() #@todo
                    
    

    def model_errorcondition_delete(self, id, guid='', **kwargs):
        """
        remove the model errorcondition with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.errorcondition.delete(guid=guid, id=id)
                    
    

    def model_errorcondition_find(self, query='', **kwargs):
        """
        query to model errorcondition
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.errorcondition.find(query)            
                    
    

    def model_errorcondition_get(self, id, guid='', **kwargs):
        """
        get model errorcondition with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.errorcondition.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_errorcondition_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.errorcondition.list()            
                    
    

    def model_errorcondition_new(self, **kwargs):
        """
        Create a new modelobjecterrorcondition instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.errorcondition.new()
                    
    

    def model_errorcondition_set(self, data='', **kwargs):
        """
        Saves model errorcondition instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.errorcondition.set(data)            
                    
    
