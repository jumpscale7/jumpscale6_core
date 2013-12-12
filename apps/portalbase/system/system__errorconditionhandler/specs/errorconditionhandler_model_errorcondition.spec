
[actor]
	"""
	is actor to manipulate pymodel errorcondition
	"""
	method:model_errorcondition_delete
		"""
		remove the model errorcondition with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
		"""
        @tasklettemplate:modeldelete
		var:id int,None,Object identifier
        var:guid str,"",unique identifier can be used as auth key  @tags: optional
		result:bool    #True if successful, False otherwise

	method:model_errorcondition_get
		"""
		get model errorcondition with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
		"""
        @tasklettemplate:modelget
		var:id int,None,Object identifier
        var:guid str,"",unique identifier can be used as auth key  @tags: optional 
        result:object

    method:model_errorcondition_new
        """
        Create a new modelobjecterrorcondition instance and return as empty.
        A new object will be created and a new id & guid generated
        """
        @tasklettemplate:modelnew
        result:object    #the pymodel object

	method:model_errorcondition_set
		"""
		Saves model errorcondition instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
		"""
        @tasklettemplate:modelupdate
        var:data str,"",data is object to save
		result:bool    #True if successful, False otherwise

	method:model_errorcondition_find
		"""
		query to model errorcondition
        @todo how to query
        example: name=aname
        secret key needs to be given
		"""
        @tasklettemplate:modelfind
		var:query str,"",unique identifier can be used as auth key
		result:list    #list of list [[$id,$guid,$relevantpropertynames...]]

    method:model_errorcondition_list
        """
        list models, used by e.g. a datagrid
        """
        @tasklettemplate:modellist novalidation
        result:json   

    method:model_errorcondition_datatables
        """
        list models, used by e.g. a datagrid
        """
        @tasklettemplate:modeldatatables returnformat:jsonraw
        result:json   


    method:model_errorcondition_create
        """
        Create a new model
        """
        @tasklettemplate:create
        var:guid str,,is guid
        var:appname str,,name for application which generated the error condition
        var:actorname str,,name for actor which generated the error condition
        var:description str,,description for private (developer) usage
        var:descriptionpub str,,description as what can be read by endusers
        var:level int,,1:critical, 2:warning, 3:info
        var:category str,,dot notation e.g. machine.start.failed
        var:tags str,,pylabs tag string, can be used to put addtional info e.g. vmachine:2323
        var:state str, state is "NEW,"ALERT" or "CLOSED"
        var:inittime int,,first time there was an error condition linked to this alert
        var:lasttime int,,last time there was an error condition linked to this alert
        var:closetime int,,alert is closed, no longer active
        var:nrerrorconditions int,1,nr of times this error condition happened
        var:traceback str,,optional traceback info e.g. for bug
        result:json
