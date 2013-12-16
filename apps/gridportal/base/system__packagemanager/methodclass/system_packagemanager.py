from JumpScale import j
import JumpScale.grid.agentcontroller

class system_packagemanager(j.code.classGetBase()):

    def __init__(self):
        self._te = {}
        self.actorname = "packagemanager"
        self.appname = "system"
        j.core.portal.runningPortal.actorsloader.getActor('system', 'gridmanager')

    def getInstalledJPackages(self, **args):
        nodeId = args.get('nodeId')
        domain = args.get('domain', None)
        client = j.apps.system.gridmanager.getClient(nodeId)
        return client.listJPackages(domain)

    def getJPackage(self, **args):
        nodeId = args.get('nodeId')
        domain = args.get('domain')
        name = args.get('name')
        client = j.apps.system.gridmanager.getClient(nodeId)
        return client.getJPackage(domain, name)

    def start(self, **args):
        nodeId = args.get('nodeId')
        domain = args.get('domain')
        name = args.get('name')
        return j.clients.agentcontroller.execute('jumpscale', 'start_jpackage', 'computenode', domain=domain, pname=name)

    def stop(self, **args):
        nodeId = args.get('nodeId')
        domain = args.get('domain')
        name = args.get('name')
        return j.clients.agentcontroller.execute('jumpscale', 'stop_jpackage', 'computenode', domain=domain, pname=name)