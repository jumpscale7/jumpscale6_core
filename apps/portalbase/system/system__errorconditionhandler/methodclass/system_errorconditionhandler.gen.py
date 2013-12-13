from JumpScale import j

class system_errorconditionhandler(j.code.classGetBase()):
    """
    errorcondition handling
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="errorconditionhandler"
        self.appname="system"
        #system_errorconditionhandler_osis.__init__(self)
    

        pass

    def describeCategory(self, category, language, description, resolution_user, resolution_ops, **kwargs):
        """
        describe the errorcondition category (type)
        describe it as well as the possible solution
        is sorted per language
        param:category in dot notation e.g. pmachine.memfull
        param:language language id e.g. UK,US,NL,FR  (
        param:description describe this errorcondition category
        param:resolution_user describe this errorcondition solution that the user can do himself
        param:resolution_ops describe this errorcondition solution that the operator can do himself to try and recover from the situation
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method describeCategory")
    

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
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_errorcondition_create")
    

    def model_errorcondition_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_errorcondition_datatables")
    

    def model_errorcondition_delete(self, id, guid='', **kwargs):
        """
        remove the model errorcondition with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_errorcondition_delete")
    

    def model_errorcondition_find(self, query='', **kwargs):
        """
        query to model errorcondition
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_errorcondition_find")
    

    def model_errorcondition_get(self, id, guid='', **kwargs):
        """
        get model errorcondition with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_errorcondition_get")
    

    def model_errorcondition_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_errorcondition_list")
    

    def model_errorcondition_new(self, **kwargs):
        """
        Create a new modelobjecterrorcondition instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_errorcondition_new")
    

    def model_errorcondition_set(self, data='', **kwargs):
        """
        Saves model errorcondition instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_errorcondition_set")
    
