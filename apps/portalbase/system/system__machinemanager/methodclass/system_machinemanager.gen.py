from JumpScale import j

class system_machinemanager(j.code.classGetBase()):
    """
    manage the machines in a physical network
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="machinemanager"
        self.appname="system"
        #system_machinemanager_osis.__init__(self)
    

        pass

    def executeAction(self, id, name, organization, arguments, **kwargs):
        """
        execute an action on a machine
        param:id unique id of machine
        param:name name of action
        param:organization name of action
        param:arguments arguments to the action (params)
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method executeAction")
    

    def initOverSSH(self, name, organization, ipaddr, passwd, login='root', **kwargs):
        """
        will ssh into the machin and install jumpscale & bootstrap the machine
        will also fetch the info from the machine & populate local portal
        param:name optional name of machine
        param:organization optional organization of machine
        param:ipaddr ip addr to start from
        param:login login to that machine default=root
        param:passwd passwd to that machine
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method initOverSSH")
    

    def initSelf(self, name, organization, **kwargs):
        """
        init local machine into db, give optional name & org info
        param:name name of action
        param:organization name of action
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method initSelf")
    

    def model_machine_create(self, name, descr, mac, nics, disks, realityUpdateEpoch, status, hostName, hypervisorTypes, acl, cloudspaceId, networkGatewayIPv4, organization, roles, cpus=1, **kwargs):
        """
        Create a new model
        param:name name as given by sysadmin but needs to be unique (in beginning is organization__hostname if it does not exist yet)
        param:descr 
        param:mac mac of first physical network adaptor (ethernet), serves as unique id for machine
        param:nics List of id Nic objects (network interfaces) attached to this machine
        param:disks List of id Disk objects attached to this machine
        param:realityUpdateEpoch in epoch last time this object has been updated from reality
        param:status status of the vm (HALTED;INIT;RUNNING;TODELETE;SNAPSHOT;EXPORT)
        param:hostName hostname of the machine as specified by OS; is name in case no hostname is provided
        param:cpus number of cpu assigned to the vm default=1
        param:hypervisorTypes hypervisor running this machine (VMWARE;HYPERV;KVM)
        param:acl access control list
        param:cloudspaceId id of space which holds this machine
        param:networkGatewayIPv4 IP address of the gateway for this machine
        param:organization free dot notation organization name
        param:roles roles for machine
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_machine_create")
    

    def model_machine_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_machine_datatables")
    

    def model_machine_delete(self, id, guid='', **kwargs):
        """
        remove the model machine with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_machine_delete")
    

    def model_machine_find(self, query='', **kwargs):
        """
        query to model machine
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_machine_find")
    

    def model_machine_get(self, id, guid='', **kwargs):
        """
        get model machine with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_machine_get")
    

    def model_machine_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_machine_list")
    

    def model_machine_new(self, **kwargs):
        """
        Create a new modelobjectmachine instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_machine_new")
    

    def model_machine_set(self, data='', **kwargs):
        """
        Saves model machine instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_machine_set")
    

    def model_network_create(self, name, descr, vlanId, subnet, netmask, nameservers, organization, **kwargs):
        """
        Create a new model
        param:name name as given by customer
        param:descr 
        param:vlanId ethernet vlan tag
        param:subnet subnet of the network
        param:netmask netmask of the network
        param:nameservers Nameservers
        param:organization free dot notation organization name if applicable
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_network_create")
    

    def model_network_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_network_datatables")
    

    def model_network_delete(self, id, guid='', **kwargs):
        """
        remove the model network with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_network_delete")
    

    def model_network_find(self, query='', **kwargs):
        """
        query to model network
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_network_find")
    

    def model_network_get(self, id, guid='', **kwargs):
        """
        get model network with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_network_get")
    

    def model_network_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_network_list")
    

    def model_network_new(self, **kwargs):
        """
        Create a new modelobjectnetwork instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_network_new")
    

    def model_network_set(self, data='', **kwargs):
        """
        Saves model network instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method model_network_set")
    
