from JumpScale import j

class system_machinemanager_osis(j.code.classGetBase()):
    """
    manage the machines in a physical network
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.db=self.dbmem
        self.dbfs=j.db.keyvaluestore.getFileSystemStore(namespace="machinemanager", baseDir=None,serializers=[j.db.serializers.getSerializerType('j')])
    

        pass

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
        
        machine = self.models.machine.new()
        machine.name = name
        machine.descr = descr
        machine.mac = mac
        machine.nics = nics
        machine.disks = disks
        machine.realityUpdateEpoch = realityUpdateEpoch
        machine.status = status
        machine.hostName = hostName
        machine.cpus = cpus
        machine.hypervisorTypes = hypervisorTypes
        machine.acl = acl
        machine.cloudspaceId = cloudspaceId
        machine.networkGatewayIPv4 = networkGatewayIPv4
        machine.organization = organization
        machine.roles = roles
        
        return self.models.machine.set(machine)
                
    

    def model_machine_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.machine.datatables() #@todo
                    
    

    def model_machine_delete(self, id, guid='', **kwargs):
        """
        remove the model machine with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.machine.delete(guid=guid, id=id)
                    
    

    def model_machine_find(self, query='', **kwargs):
        """
        query to model machine
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.machine.find(query)            
                    
    

    def model_machine_get(self, id, guid='', **kwargs):
        """
        get model machine with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.machine.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_machine_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.machine.list()            
                    
    

    def model_machine_new(self, **kwargs):
        """
        Create a new modelobjectmachine instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.machine.new()
                    
    

    def model_machine_set(self, data='', **kwargs):
        """
        Saves model machine instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.machine.set(data)            
                    
    

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
        
        network = self.models.network.new()
        network.name = name
        network.descr = descr
        network.vlanId = vlanId
        network.subnet = subnet
        network.netmask = netmask
        network.nameservers = nameservers
        network.organization = organization
        
        return self.models.network.set(network)
                
    

    def model_network_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.network.datatables() #@todo
                    
    

    def model_network_delete(self, id, guid='', **kwargs):
        """
        remove the model network with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.network.delete(guid=guid, id=id)
                    
    

    def model_network_find(self, query='', **kwargs):
        """
        query to model network
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.network.find(query)            
                    
    

    def model_network_get(self, id, guid='', **kwargs):
        """
        get model network with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.network.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_network_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.network.list()            
                    
    

    def model_network_new(self, **kwargs):
        """
        Create a new modelobjectnetwork instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.network.new()
                    
    

    def model_network_set(self, data='', **kwargs):
        """
        Saves model network instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.network.set(data)            
                    
    
