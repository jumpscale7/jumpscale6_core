
[actor]
	"""
	is actor to manipulate pymodel network
	"""
	method:model_network_delete
		"""
		remove the model network with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
		"""
        @tasklettemplate:modeldelete
		var:id int,None,Object identifier
        var:guid str,"",unique identifier can be used as auth key  @tags: optional
		result:bool    #True if successful, False otherwise

	method:model_network_get
		"""
		get model network with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
		"""
        @tasklettemplate:modelget
		var:id int,None,Object identifier
        var:guid str,"",unique identifier can be used as auth key  @tags: optional 
        result:object

    method:model_network_new
        """
        Create a new modelobjectnetwork instance and return as empty.
        A new object will be created and a new id & guid generated
        """
        @tasklettemplate:modelnew
        result:object    #the pymodel object

	method:model_network_set
		"""
		Saves model network instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
		"""
        @tasklettemplate:modelupdate
        var:data str,"",data is object to save
		result:bool    #True if successful, False otherwise

	method:model_network_find
		"""
		query to model network
        @todo how to query
        example: name=aname
        secret key needs to be given
		"""
        @tasklettemplate:modelfind
		var:query str,"",unique identifier can be used as auth key
		result:list    #list of list [[$id,$guid,$relevantpropertynames...]]

    method:model_network_list
        """
        list models, used by e.g. a datagrid
        """
        @tasklettemplate:modellist novalidation
        result:json   

    method:model_network_datatables
        """
        list models, used by e.g. a datagrid
        """
        @tasklettemplate:modeldatatables returnformat:jsonraw
        result:json   


    method:model_network_create
        """
        Create a new model
        """
        @tasklettemplate:create
        var:name str,,name as given by customer
        var:descr str,,
        var:vlanId str,,ethernet vlan tag
        var:subnet str,,subnet of the network
        var:netmask str,,netmask of the network
        var:nameservers list(str),,Nameservers
        var:organization str,,free dot notation organization name if applicable
        result:json
