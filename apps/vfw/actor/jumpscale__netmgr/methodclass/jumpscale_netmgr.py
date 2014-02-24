from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.lib.lxc
import JumpScale.baselib.serializers

class jumpscale_netmgr(j.code.classGetBase()):
    """
    net manager
    
    """
    def __init__(self):
        
        self._te = {}
        self.actorname = "netmgr"
        self.appname = "jumpscale"
        #jumpscale_netmgr_osis.__init__(self)
        self.client = j.core.osis.getClient(user='root')
        self.osisclient = j.core.osis.getClientForCategory(self.client, 'vfw', 'virtualfirewall')
        self.agentcontroller = j.clients.agentcontroller.get()
        self.json = j.db.serializers.getSerializerType('j')

    def fw_check(self, fwid, gid, **kwargs):
        """
        will do some checks on firewall to see is running, is reachable over ssh, is connected to right interfaces
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisclient.get(fwid)
        host = j.system.platform.lxc.getIp(fwobj.name)
        return j.system.net.pingMachine(host, 5)
    

    def fw_create(self, domain, name, gid, nid, masquerade, **kwargs):
        """
        param:domain needs to be unique name of a domain,e.g. a group, space, ... (just to find the FW back)
        param:name needs to be unique name of vfirewall
        param:gid grid id
        param:nid node id
        param:masquerade do you want to allow masquerading?
        """
        self.agentcontroller.executeJumpScript('jumpscale', 'vfs_create', args={'name': name}, wait=False)
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
        fwobj = self.osisclient.get(fwid)
        self.agentcontroller.executeJumpScript('jumpscale', 'vfs_delete', args={'name': fwobj.name}, wait=False)
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
        self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig', args={'name': fwobj.name, 'fwobject': self.json.dumps(fwobj)}, wait=False)
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
                self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig', args={'name': fwobj.name, 'fwobject': self.json.dumps(fwobj)}, wait=False)
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

    def fw_list(self, gid, domain=None, **kwargs):
        """
        param:gid grid id
        param:domain if not specified then all domains
        """
        result = list()
        vfws = self.osisclient.list()
        fields = ('domain', 'name', 'gid', 'guid')
        for vfwid in vfws:
            vfwdict = {}
            vfw = self.osisclient.get(vfwid)
            for field in fields:
                vfwdict[field] = getattr(vfw, field, None)
            if not domain and str(vfw.gid) == str(gid):
                result.append(vfwdict)
            if domain and vfw.domain == domain and str(vfw.gid) == str(gid):
                result.append(vfwdict)
        return result
    

    def fw_start(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisclient.get(fwid)
        self.agentcontroller.executeJumpScript('jumpscale', 'fw_action', args={'name': fwobj.name, 'action': 'start'}, wait=False)
        return True
    

    def fw_stop(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisclient.get(fwid)
        self.agentcontroller.executeJumpScript('jumpscale', 'fw_action', args={'name': fwobj.name, 'action': 'stop'}, wait=False)
        return True
    

    def ws_forward_create(self, wsid, gid, sourceurl, desturls, **kwargs):
        """
        param:wsid firewall id
        param:gid grid id
        param:sourceurl url which will match (e.g. http://www.incubaid.com:80/test/)
        param:desturls url which will be forwarded to (e.g. http://192.168.10.1/test/) can be more than 1 then loadbalancing; if only 1 then like a portforward but matching on url
        """
        wsfobj = self.osisclient.get(wsid)
        rule = wsfobj.new_wsForwardRule()
        rule.url = sourceurl
        rule.toUrls = desturls
        self.osisclient.set(wsfobj)
        return True
    

    def ws_forward_delete(self, wsid, gid, sourceurl, desturls, **kwargs):
        """
        param:wsid firewall id
        param:gid grid id
        param:sourceurl url which will match (e.g. http://www.incubaid.com:80/test/)
        param:desturls url which will be forwarded to
        """
        vfws = self.osisclient.get(wsid)
        wsfr = vfws.wsForwardRules
        for rule in wsfr:
            if rule.url == sourceurl:
                desturls = desturls.split(',')
                urls = rule.toUrls.split(',')
                for dest in desturls:
                    if dest in rule.toUrls:
                        urls.remove(dest)
                rule.toUrls = ','.join(urls)
                if len(urls) == 0:
                    wsfr.remove(rule)
        return True
    

    def ws_forward_list(self, wsid, gid, **kwargs):
        """
        list all loadbalancing rules (HTTP ONLY),
        ws stands for webserver
        is list of list [[$sourceurl,$desturl],..]
        can be 1 in which case its like simple forwarding, if more than 1 then is loadbalancing
        param:wsid firewall id (is also the loadbalancing webserver)
        param:gid grid id
        """
        result = list()
        vfws = self.osisclient.get(wsid)
        wsfr = vfws.wsForwardRules
        for rule in wsfr:
            result.append([rule.url, rule.toUrls])
        return result
    
