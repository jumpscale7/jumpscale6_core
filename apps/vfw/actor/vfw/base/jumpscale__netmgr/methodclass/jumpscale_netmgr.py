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
        self.osisvfw = j.core.osis.getClientForCategory(self.client, 'vfw', 'virtualfirewall')
        self.agentcontroller = j.clients.agentcontroller.get()
        self.json = j.db.serializers.getSerializerType('j')

    def fw_check(self, fwid, gid, **kwargs):
        """
        will do some checks on firewall to see is running, is reachable over ssh, is connected to right interfaces
        param:fwid firewall id
        param:gid grid id
        """        
        fwobj = self.osisvfw.get(fwid)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name)}
        return self.agentcontroller.executeJumpScript('jumpscale', 'vfs_checkstatus', nid=fwobj.nid, args=args)['result']

    def fw_create(self, domain, name, gid, nid, masquerade,login, password, host, type, **kwargs):
        """
        param:domain needs to be unique name of a domain,e.g. a group, space, ... (just to find the FW back)
        param:name needs to be unique name of vfirewall
        param:gid grid id
        param:nid node id
        param:masquerade do you want to allow masquerading?
        param:login admin login to the firewall
        param:password admin password to the firewall
        param:host management address to manage the firewall
        param:type type of firewall e.g routeros, ...
        """
        fwobj = self.osisvfw.new()
        fwobj.domain = domain
        fwobj.name = name
        fwobj.gid = gid
        fwobj.nid = nid
        fwobj.masquerade = masquerade
        fwobj.host = host
        fwobj.username = login
        fwobj.password = password
        fwobj.type =  type
        self.osisvfw.set(fwobj)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name)}
        if type == 'routeros':
            return True
        else:
            return self.agentcontroller.executeJumpScript('jumpscale', 'vfs_create', nid=nid, args=args)['result']

    def fw_delete(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisvfw.get(fwid)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name)}
        result = self.agentcontroller.executeJumpScript('jumpscale', 'vfs_delete', nid=fwobj.nid, args=args)['result']
        if result:
            self.osisvfw.delete(fwid)
        return result

    def _applyconfig(self, nid, args):
        if args['fwobject']['type'] == 'routeros':
            result = self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig_routeros', nid=nid, args=args)['result']
        else:
            result = self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig', nid=nid, args=args)['result']
        return result


    def fw_forward_create(self, fwid, gid, fwip, fwport, destip, destport, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        param:fwip str,,adr on fw which will be visible to extenal world
        param:fwport str,,port on fw which will be visble to external world
        param:destip adr where we forward to e.g. a ssh server in DMZ
        param:destport port where we forward to e.g. a ssh server in DMZ
        """
        fwobj = self.osisvfw.get(fwid)
        rule = fwobj.new_tcpForwardRule()
        rule.fromAddr = fwip
        rule.fromPort = fwport
        rule.toAddr = destip
        rule.toPort = destport
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': fwobj.obj2dict()}
        result = self._applyconfig(fwobj.nid, args)
        if result:
            self.osisvfw.set(fwobj)
        return result

    def fw_forward_delete(self, fwid, gid, fwip, fwport, destip, destport, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        param:fwip str,,adr on fw which will be visible to extenal world
        param:fwport port on fw which will be visble to external world
        param:destip adr where we forward to e.g. a ssh server in DMZ
        param:destport port where we forward to e.g. a ssh server in DMZ
        """
        fwobj = self.osisvfw.get(fwid)
        for rule in fwobj.tcpForwardRules:
            if rule.fromPort == fwport and rule.toAddr == destip and rule.toPort == destport and rule.fromAddr == fwip:
                fwobj.tcpForwardRules.remove(rule)
                args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': fwobj.obj2dict()}
                result = self._applyconfig(fwobj.nid, args)
                if result:
                    self.osisvfw.set(fwobj)
        return result
    

    def fw_forward_list(self, fwid, gid, **kwargs):
        """
        list all portformarding rules,
        is list of list [[$fwport,$destip,$destport]]
        1 port on source can be forwarded to more ports at back in which case the FW will do loadbalancing
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisvfw.get(fwid)
        result = list()
        for rule in fwobj.tcpForwardRules:
            result.append({'publicIp':rule.fromAddr, 'publicPort':rule.fromPort, 'localIp':rule.toAddr, 'localPort':rule.toPort})
        return result

    def fw_list(self, gid, domain=None, **kwargs):
        """
        param:gid grid id
        param:domain if not specified then all domains
        """
        result = list()
        vfws = self.osisvfw.list()
        fields = ('domain', 'name', 'gid', 'nid', 'guid')
        for vfwid in vfws:
            vfwdict = {}
            vfw = self.osisvfw.get(vfwid)
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
        fwobj = self.osisvfw.get(fwid)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'action': 'start'}
        return self.agentcontroller.executeJumpScript('jumpscale', 'fw_action', nid=fwobj.nid, args=args)['result']

    def fw_stop(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisvfw.get(fwid)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'action': 'stop'}
        self.agentcontroller.executeJumpScript('jumpscale', 'fw_action', nid=fwobj.nid, args=args, wait=False)
        return True
    

    def ws_forward_create(self, wsid, gid, sourceurl, desturls, **kwargs):
        """
        param:wsid firewall id
        param:gid grid id
        param:sourceurl url which will match (e.g. http://www.incubaid.com:80/test/)
        param:desturls url which will be forwarded to (e.g. http://192.168.10.1/test/) can be more than 1 then loadbalancing; if only 1 then like a portforward but matching on url
        """
        wsfobj = self.osisvfw.get(wsid)
        rule = wsfobj.new_wsForwardRule()
        rule.url = sourceurl
        rule.toUrls = desturls
        self.osisvfw.set(wsfobj)
        self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig', nid=wsfobj.nid, args={'name': wsfobj.name, 'fwobject': wsfobj.obj2dict()}, wait=False)
        return True
    

    def ws_forward_delete(self, wsid, gid, sourceurl, desturls, **kwargs):
        """
        param:wsid firewall id
        param:gid grid id
        param:sourceurl url which will match (e.g. http://www.incubaid.com:80/test/)
        param:desturls url which will be forwarded to
        """
        vfws = self.osisvfw.get(wsid)
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
        args = {'name': '%s_%s' % (vfws.domain, vfws.name), 'action': 'start'}
        self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig', nid=vfws.nid, args={'name': vfws.name, 'fwobject': vfws.obj2dict()}, wait=False)
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
        vfws = self.osisvfw.get(wsid)
        wsfr = vfws.wsForwardRules
        for rule in wsfr:
            result.append([rule.url, rule.toUrls])
        return result
    
