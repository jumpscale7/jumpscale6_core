from JumpScale import j
import JumpScale.grid.agentcontroller

class system_packagemanager(j.code.classGetBase()):

    def __init__(self):
        self._te = {}
        self.actorname = "packagemanager"
        self.appname = "system"
        j.clients.agentcontroller.client.loadJumpscripts()
        j.core.portal.runningPortal.actorsloader.getActor('system', 'gridmanager')

    def getInstalledJPackages(self, **args):
        nodeId = args.get('nodeId')
        domain = args.get('domain', None)
        client = j.apps.system.gridmanager.getClient(nodeId)
        return client.listJPackages(domain)

    def getJPackage(self, **args):
        nodeId = args.get('nodeId')
        gid, _, _ = j.application.whoAmI
        roles = "node.%i.%i" % (gid, nodeId)
        domain = args.get('domain', None)
        name = args.get('pname', None)
        version = args.get('version', None)
        return j.clients.agentcontroller.execute('jumpscale', 'jpackage_info', roles, domain=domain, pname=name, version=version)

    def getPackageDescription(self, **args):
        nodeId = args.get('nodeId')
        gid, _, _ = j.application.whoAmI
        roles = "node.%i.%i" % (gid, nodeId)
        domain = args.get('domain', None)
        name = args.get('pname', None)
        version = args.get('version', None)
        return j.clients.agentcontroller.execute('jumpscale', 'jpackage_descr', roles, domain=domain, pname=name, version=version)

    def action(self, **args):
        nodeId = args.get('nodeId')
        gid, _, _ = j.application.whoAmI
        roles = "node.%i.%i" % (gid, nodeId)
        domain = args.get('domain', None)
        name = args.get('pname', None)
        action = args.get('action', None)
        version = args.get('version', None)
        return j.clients.agentcontroller.execute('jumpscale', 'jpackage_action', roles, domain=domain, pname=name, version=version, action=action)