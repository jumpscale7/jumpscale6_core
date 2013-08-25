from JumpScale import j
from system_machinemanager_osis import system_machinemanager_osis


class system_machinemanager(system_machinemanager_osis):

    """
    manage the machines in a physical network
    
    """

    def __init__(self):

        self._te = {}
        self.actorname = "machinemanager"
        self.appname = "system"
        system_machinemanager_osis.__init__(self)

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
        # put your code here to implement this method
        raise NotImplementedError("not implemented method executeAction")

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
        # put your code here to implement this method
        raise NotImplementedError("not implemented method initOverSSH")

    def initSelf(self, name="", organization="", **kwargs):
        """
        init local machine into db, give optional name & org info
        param:name name of action
        param:organization name of action
        result bool 
        
        """
        # put your code here to implement this method
        machine = self.models.machine.new()
        if name != "":
            machine.name = name
        else:
            machine = j.system.net.getHostname()
        machine.hostname = j.system.net.getHostname()
        if organization != "":
            machine.organization = organization
        else:
            machine.organization = "default"
        machine.status = "NEW"

        machine.mac = j.application.getUniqueMachineId()

        nics = j.system.net.getNics()
        for nic in nics:
            if nic.find("eth") == 0 or nic.find("br") == 0:
                nicobj = machine.new_nic()
                nicobj.deviceName = nic
                mac = j.system.net.getMacAddress(nic)
                nicobj.macAddress = mac
                if j.system.net.isNicConnected(nic):
                    nicobj.status = "ACTIVE"
                else:
                    nicobj.status = "DOWN"
                nicobj.ipAddresses = [item[0] for item in j.system.net.getIpAddress(nic)]
                nicobj.realityUpdateEpoch = j.base.time.getTimeEpoch()

        #@todo do same for disks (aren't there any extensions for it?)

        query = {
            "query": {"bool": {"must": [{"term": {"machine.mac": machine.mac}}], "must_not": [], "should": []}}, "from": 0, "size": 50, "sort": [], "facets": {}}
        result = self.model_machine_find(query=query)

        if len(result["result"]) > 0:
            # a machine with that mac is already in db
            machinefound = result["result"][0]["_source"]
            machine.guid = machinefound["guid"]
            machine.id = machinefound["id"]

        self.model_machine_set(data=machine)

        return machine.id
