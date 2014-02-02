from JumpScale import j

class jumpscale_netmgr(j.code.classGetBase()):
    """
    net manager
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="netmgr"
        self.appname="jumpscale"
        #jumpscale_netmgr_osis.__init__(self)
        self.client = j.core.osis.getClient(user='root')
        self.osisclient =j.core.osis.getClientForCategory(self.client, 'vfw', 'virtualfirewall')

    def fw_check(self, fwid, gid, **kwargs):
        """
        will do some checks on firewall to see is running, is reachable over ssh, is connected to right interfaces
        param:fwid firewall id
        param:gid grid id
        """
        return True
    

    def fw_create(self, domain, name, gid, nid, masquerade, **kwargs):
        """
        param:domain needs to be unique name of a domain,e.g. a group, space, ... (just to find the FW back)
        param:name needs to be unique name of vfirewall
        param:gid grid id
        param:nid node id
        param:masquerade do you want to allow masquerading?
        """
        fwobj = self.osisclient.new()
        fwobj.domain = domain
        fwobj.name = name
        fwobj.gid = gid
        fwobj.nid = nid
        fwobj.masquerade = masquerade
        self.osisclient.set(fwobj)
        return fwobj.guid

    def fw_delete(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        self.osisclient.delete(fwid)
        return True
    

    def fw_forward_create(self, fwid, gid, fwport, destip, destport, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        param:fwport port on fw which will be visble to external world
        param:destip adr where we forward to e.g. a ssh server in DMZ
        param:destport port where we forward to e.g. a ssh server in DMZ
        """
        fwobj = self.osisclient.get(fwid)
        rule = fwobj.new_tcpForwardRule()
        rule.fromPort = fwport
        rule.toAddr = destip
        rule.toPort = destport
        self.osisclient.set(fwobj)
        return True

    def fw_forward_delete(self, fwid, gid, fwport, destip, destport, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        param:fwport port on fw which will be visble to external world
        param:destip adr where we forward to e.g. a ssh server in DMZ
        param:destport port where we forward to e.g. a ssh server in DMZ
        """
        fwobj = self.osisclient.get(fwid)
        for rule in fwobj.tcpForwardRules:
            if rule.fromPort == fwport and rule.toAddr == destip and rule.toPort == destport:
                fwobj.tcpForwardRules.remove(rule)
                return True

        return False
    

    def fw_forward_list(self, fwid, gid, **kwargs):
        """
        list all portformarding rules,
        is list of list [[$fwport,$destip,$destport]]
        1 port on source can be forwarded to more ports at back in which case the FW will do loadbalancing
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisclient.get(fwid)
        result = list()
        for rule in fwobj.tcpForwardRules:
            result.append([rule.fromPort, rule.toAddr, rule.toPort])

        return result

    def fw_list(self, gid, domain, **kwargs):
        """
        param:gid grid id
        param:domain if not specified then all domains
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method fw_list")
    

    def fw_start(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method fw_start")
    

    def fw_stop(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method fw_stop")
    

    def ws_forward_create(self, wsid, gid, sourceurl, desturls, **kwargs):
        """
        param:wsid firewall id
        param:gid grid id
        param:sourceurl url which will match (e.g. http://www.incubaid.com:80/test/)
        param:desturls url which will be forwarded to (e.g. http://192.168.10.1/test/) can be more than 1 then loadbalancing; if only 1 then like a portforward but matching on url
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method ws_forward_create")
    

    def ws_forward_delete(self, wsid, gid, sourceurl, desturls, **kwargs):
        """
        param:wsid firewall id
        param:gid grid id
        param:sourceurl url which will match (e.g. http://www.incubaid.com:80/test/)
        param:desturls url which will be forwarded to
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method ws_forward_delete")
    

    def ws_forward_list(self, wsid, gid, **kwargs):
        """
        list all loadbalancing rules (HTTP ONLY),
        ws stands for webserver
        is list of list [[$sourceurl,$desturl],..]
        can be 1 in which case its like simple forwarding, if more than 1 then is loadbalancing
        param:wsid firewall id (is also the loadbalancing webserver)
        param:gid grid id
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method ws_forward_list")
    
