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

    def getInstalledJPackages(self, **args):
        nodeId = args.get('nodeId')
        domain = args.get('domain', None)
        client = j.apps.system.gridmanager.getClient(nodeId)
        return client.listJPackages(domain)

    def getJPackage(self, **args):
        nodeId = args.get('nodeId')
        roles = "node.%s.%s" % (self.gid, nodeId)
        domain = args.get('domain', None)
        name = args.get('pname', None)
        version = args.get('version', None)
        jp= j.clients.agentcontroller.execute('jumpscale', 'jpackage_info', roles, domain=domain, pname=name, version=version)
        return jp


    def getPackageDescription(self, **args):
        nodeId = args.get('nodeId')
        roles = "node.%s.%s" % (self.gid, nodeId)
        domain = args.get('domain', None)
        name = args.get('pname', None)
        version = args.get('version', None)
        return j.clients.agentcontroller.execute('jumpscale', 'jpackage_descr', roles, domain=domain, pname=name, version=version)

    def action(self, **args):
        nodeId = args.get('nodeId')
        roles = "node.%s.%s" % (self.gid, nodeId)
        domain = args.get('domain', None)
        name = args.get('pname', None)
        action = args.get('action', None)
        version = args.get('version', None)
        return j.clients.agentcontroller.execute('jumpscale', 'jpackage_action', roles, domain=domain, pname=name, version=version, wait=False, action=action)

    def getBlobs(self, **args):
        nodeId = args.get('nodeId')
        domain = args.get('domain', None)
        name = args.get('pname', None)
        version = args.get('version', None)
        roles = "node.%s.%s" % (self.gid, nodeId)
        return j.clients.agentcontroller.execute('jumpscale', 'jpackage_blobs', roles, domain=domain, pname=name, version=version)

    def getBlobContents(self, **args):
        nodeId = args.get('nodeId')
        domain = args.get('domain', None)
        name = args.get('pname', None)
        version = args.get('version', None)
        platform = args.get('platform')
        ttype = args.get('ttype')
        roles = "node.%s.%s" % (self.gid, nodeId)
        blobcontent =  j.clients.agentcontroller.execute('jumpscale', 'jpackage_blobdata', roles, domain=domain, pname=name, version=version, platform=platform, ttype=ttype)['result']
        import json
        return json.loads(blobcontent)['result']