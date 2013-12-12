
[actor]
	"""
	is actor to manipulate pymodel history
	"""
	method:model_history_delete
		"""
		remove the model history with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
		"""
        @tasklettemplate:modeldelete
		var:id int,None,Object identifier
        var:guid str,"",unique identifier can be used as auth key  @tags: optional
		result:bool    #True if successful, False otherwise

	method:model_history_get
		"""
		get model history with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
		"""
        @tasklettemplate:modelget
		var:id int,None,Object identifier
        var:guid str,"",unique identifier can be used as auth key  @tags: optional 
        result:object

    method:model_history_new
        """
        Create a new modelobjecthistory instance and return as empty.
        A new object will be created and a new id & guid generated
        """
        @tasklettemplate:modelnew
        result:object    #the pymodel object

	method:model_history_set
		"""
		Saves model history instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
		"""
        @tasklettemplate:modelupdate
        var:data str,"",data is object to save
		result:bool    #True if successful, False otherwise

	method:model_history_find
		"""
		query to model history
        @todo how to query
        example: name=aname
        secret key needs to be given
		"""
        @tasklettemplate:modelfind
		var:query str,"",unique identifier can be used as auth key
		result:list    #list of list [[$id,$guid,$relevantpropertynames...]]

    method:model_history_list
        """
        list models, used by e.g. a datagrid
        """
        @tasklettemplate:modellist novalidation
        result:json   

    method:model_history_datatables
        """
        list models, used by e.g. a datagrid
        """
        @tasklettemplate:modeldatatables returnformat:jsonraw
        result:json   


    method:model_history_create
        """
        Create a new model
        """
        @tasklettemplate:create
        var:guid str,,is unique name (in dot notation)
        var:month_5min dict(float),, dict of measurements per 5 min, keep 31 days +1 h : 8929 items in dict
        var:year_hour dict(list),, dict of measurements per hour (per hour keep [nritems,total,min,max]), keep 12 months +1 day: 8761 items in dict
        result:json
