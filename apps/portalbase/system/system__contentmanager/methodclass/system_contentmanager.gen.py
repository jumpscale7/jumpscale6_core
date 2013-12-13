from JumpScale import j

class system_contentmanager(j.code.classGetBase()):
    """
    this actor manages all content on the wiki
    can e.g. notify wiki/appserver of updates of content
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="contentmanager"
        self.appname="system"
        #system_contentmanager_osis.__init__(self)
    

        pass

    def bitbucketreload(self, spacename, **kwargs):
        """
        Reload all spaces from bitbucket post
        param:spacename 
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method bitbucketreload")
    

    def getActors(self, **kwargs):
        """
        result list(str) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getActors")
    

    def getActorsWithPaths(self, **kwargs):
        """
        result list([name,path]) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getActorsWithPaths")
    

    def getBuckets(self, **kwargs):
        """
        result list(str) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getBuckets")
    

    def getBucketsWithPaths(self, **kwargs):
        """
        result list([name,path]) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getBucketsWithPaths")
    

    def getContentDirsWithPaths(self, **kwargs):
        """
        return root dirs of content (actors,buckets,spaces)
        result list([name,path]) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getContentDirsWithPaths")
    

    def getSpaces(self, **kwargs):
        """
        result list(str) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getSpaces")
    

    def getSpacesWithPaths(self, **kwargs):
        """
        result list([name,path]) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getSpacesWithPaths")
    

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
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_actor_create")
    

    def model_actor_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_actor_datatables")
    

    def model_actor_delete(self, id, guid='', **kwargs):
        """
        remove the model actor with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_actor_delete")
    

    def model_actor_find(self, query='', **kwargs):
        """
        query to model actor
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_actor_find")
    

    def model_actor_get(self, id, guid='', **kwargs):
        """
        get model actor with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_actor_get")
    

    def model_actor_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_actor_list")
    

    def model_actor_new(self, **kwargs):
        """
        Create a new modelobjectactor instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_actor_new")
    

    def model_actor_set(self, data='', **kwargs):
        """
        Saves model actor instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_actor_set")
    

    def model_bucket_create(self, id, path, acl, **kwargs):
        """
        Create a new model
        param:id 
        param:path 
        param:acl dict with key the group or username; and the value is a string
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_bucket_create")
    

    def model_bucket_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_bucket_datatables")
    

    def model_bucket_delete(self, id, guid='', **kwargs):
        """
        remove the model bucket with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_bucket_delete")
    

    def model_bucket_find(self, query='', **kwargs):
        """
        query to model bucket
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_bucket_find")
    

    def model_bucket_get(self, id, guid='', **kwargs):
        """
        get model bucket with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_bucket_get")
    

    def model_bucket_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_bucket_list")
    

    def model_bucket_new(self, **kwargs):
        """
        Create a new modelobjectbucket instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_bucket_new")
    

    def model_bucket_set(self, data='', **kwargs):
        """
        Saves model bucket instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_bucket_set")
    

    def model_space_create(self, id, path, acl, **kwargs):
        """
        Create a new model
        param:id is name of space
        param:path 
        param:acl dict with key the group or username; and the value is a string
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_space_create")
    

    def model_space_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_space_datatables")
    

    def model_space_delete(self, id, guid='', **kwargs):
        """
        remove the model space with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_space_delete")
    

    def model_space_find(self, query='', **kwargs):
        """
        query to model space
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_space_find")
    

    def model_space_get(self, id, guid='', **kwargs):
        """
        get model space with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_space_get")
    

    def model_space_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_space_list")
    

    def model_space_new(self, **kwargs):
        """
        Create a new modelobjectspace instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_space_new")
    

    def model_space_set(self, data='', **kwargs):
        """
        Saves model space instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_space_set")
    

    def modelobjectlist(self, appname, actorname, modelname, key, **kwargs):
        """
        @todo describe what the goal is of this method
        param:appname 
        param:actorname 
        param:modelname 
        param:key 
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method modelobjectlist")
    

    def modelobjectupdate(self, appname, actorname, key, **kwargs):
        """
        post args with ref_$id which refer to the key which is stored per actor in the cache
        param:appname 
        param:actorname 
        param:key 
        result html 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method modelobjectupdate")
    

    def notifyActorDelete(self, id, **kwargs):
        """
        param:id id of space which changed
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyActorDelete")
    

    def notifyActorModification(self, id, **kwargs):
        """
        param:id id of actor which changed
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyActorModification")
    

    def notifyActorNew(self, path, name, **kwargs):
        """
        param:path path of content which got changed
        param:name name
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyActorNew")
    

    def notifyActorNewDir(self, actorname, path, actorpath='', **kwargs):
        """
        param:actorname 
        param:actorpath  default=
        param:path 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyActorNewDir")
    

    def notifyBucketDelete(self, id, **kwargs):
        """
        param:id id of bucket which changed
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyBucketDelete")
    

    def notifyBucketModification(self, id, **kwargs):
        """
        param:id id of bucket which changed
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyBucketModification")
    

    def notifyBucketNew(self, path, name, **kwargs):
        """
        param:path path of content which got changed
        param:name name
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyBucketNew")
    

    def notifyFiledir(self, path, **kwargs):
        """
        param:path path of content which got changed
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifyFiledir")
    

    def notifySpaceDelete(self, id, **kwargs):
        """
        param:id id of space which changed
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifySpaceDelete")
    

    def notifySpaceModification(self, id, **kwargs):
        """
        param:id id of space which changed
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifySpaceModification")
    

    def notifySpaceNew(self, path, name, **kwargs):
        """
        param:path path of content which got changed
        param:name name
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method notifySpaceNew")
    

    def notifySpaceNewDir(self, spacename, path, spacepath='', **kwargs):
        """
        param:spacename 
        param:spacepath  default=
        param:path 
        
        """
        args={}
        args["spacename"]=spacename
        args["spacepath"]=spacepath
        args["path"]=path
        return self._te["notifySpaceNewDir"].execute4method(args,params={},actor=self)
    

    def prepareActorSpecs(self, app, actor, **kwargs):
        """
        compress specs for specific actor and targz in appropriate download location
        param:app name of app
        param:actor name of actor
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method prepareActorSpecs")
    

    def wikisave(self, cachekey, text, **kwargs):
        """
        param:cachekey key to the doc
        param:text content of file to edit
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method wikisave")
    
