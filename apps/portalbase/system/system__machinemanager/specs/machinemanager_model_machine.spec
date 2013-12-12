
[actor]
	"""
	is actor to manipulate pymodel machine
	"""
	method:model_machine_delete
		"""
		remove the model machine with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
		"""
        @tasklettemplate:modeldelete
		var:id int,None,Object identifier
        var:guid str,"",unique identifier can be used as auth key  @tags: optional
		result:bool    #True if successful, False otherwise

	method:model_machine_get
		"""
		get model machine with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
		"""
        @tasklettemplate:modelget
		var:id int,None,Object identifier
        var:guid str,"",unique identifier can be used as auth key  @tags: optional 
        result:object

    method:model_machine_new
        """
        Create a new modelobjectmachine instance and return as empty.
        A new object will be created and a new id & guid generated
        """
        @tasklettemplate:modelnew
        result:object    #the pymodel object

	method:model_machine_set
		"""
		Saves model machine instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
		"""
        @tasklettemplate:modelupdate
        var:data str,"",data is object to save
		result:bool    #True if successful, False otherwise

	method:model_machine_find
		"""
		query to model machine
        @todo how to query
        example: name=aname
        secret key needs to be given
		"""
        @tasklettemplate:modelfind
		var:query str,"",unique identifier can be used as auth key
		result:list    #list of list [[$id,$guid,$relevantpropertynames...]]

    method:model_machine_list
        """
        list models, used by e.g. a datagrid
        """
        @tasklettemplate:modellist novalidation
        result:json   

    method:model_machine_datatables
        """
        list models, used by e.g. a datagrid
        """
        @tasklettemplate:modeldatatables returnformat:jsonraw
        result:json   


    method:model_machine_create
        """
        Create a new model
        """
        @tasklettemplate:create
        var:name str,,name as given by sysadmin but needs to be unique (in beginning is organization__hostname if it does not exist yet)
        var:descr str,,
        var:mac str,,mac of first physical network adaptor (ethernet), serves as unique id for machine
        var:nics list(Nic),,List of id Nic objects (network interfaces) attached to this machine
        var:disks list(Disk),,List of id Disk objects attached to this machine
        var:realityUpdateEpoch int,,in epoch last time this object has been updated from reality
        var:status str,,status of the vm (HALTED;INIT;RUNNING;TODELETE;SNAPSHOT;EXPORT)
        var:hostName str,,hostname of the machine as specified by OS; is name in case no hostname is provided
        var:cpus int,1,number of cpu assigned to the vm
        var:hypervisorTypes list(str),,hypervisor running this machine (VMWARE;HYPERV;KVM)
        var:acl list(ACE),,access control list
        var:cloudspaceId int,,id of space which holds this machine
        var:networkGatewayIPv4 str,,IP address of the gateway for this machine
        var:organization str,,free dot notation organization name
        var:roles list(str),,roles for machine
        result:json
