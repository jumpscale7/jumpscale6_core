from JumpScale import j
import JumpScale.grid.agentcontroller

class system_packagemanager(j.code.classGetBase()):

    def __init__(self):
        self._te = {}
        self.actorname = "packagemanager"
        self.appname = "system"
        j.clients.agentcontroller.client.loadJumpscripts()
        j.core.portal.runningPortal.actorsloader.getActor('system', 'gridmanager')
        self.gid, _, _ = j.application.whoAmI


    def getJPackages(self, **args):
        nid = args.get('nid')
        domain = args.get('domain', None)
        client = j.apps.system.gridmanager.getClient(nid,"jpackages")
        return client.listJPackages(domain=domain)

    def getJPackageInfo(self, **args):
        nid = args.get('nid')
        roles = "node.%s.%s" % (self.gid, nid)
        domain = args.get('domain', None)
        name = args.get('pname', None)
        # version = args.get('version', None)
        client = j.apps.system.gridmanager.getClient(nid,"jpackages")

        jp=client.getJPackage(domain=domain, name=name)
        
        return jp

    def getJPackageFilesInfo(self, **args):
        """
        ask the right processmanager on right node to get the information (will query jpackages underneath)
        returns all relevant info about files of jpackage
        param:nid id of node
        param:domain domain name for jpackage
        param:pname name for jpackage
        result json
        """
        nid = args.get('nid')
        roles = "node.%s.%s" % (self.gid, nid)
        domain = args.get('domain', None)
        name = args.get('pname', None)
        # version = args.get('version', None)
        client = j.apps.system.gridmanager.getClient(nid,"jpackages")

        result=client.getJPackageFilesInfo(domain=domain, name=name)
        return result

    def action(self, **args):
        nid = args.get('nid')
        roles = "node.%s.%s" % (self.gid, nid)
        domain = args.get('domain', None)
        name = args.get('pname', None)
        action = args.get('action', None)
        version = args.get('version', None)
        return j.clients.agentcontroller.execute('jumpscale', 'jpackage_action', roles, domain=domain, pname=name, version=version,\
            wait=True, action=action)

