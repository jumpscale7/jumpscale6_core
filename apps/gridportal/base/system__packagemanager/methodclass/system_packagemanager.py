from JumpScale import j
import JumpScale.grid.agentcontroller

class system_packagemanager(j.code.classGetBase()):

    def __init__(self):
        self._te = {}
        self.actorname = "packagemanager"
        self.appname = "system"
        self.client = j.clients.agentcontroller.get()
        self.gid = j.application.whoAmI.gid


    def execute(self, script, nid, gid=None, **kwargs):
        return self.client.execute('jumpscale', script, nid=nid, gid=gid, args=kwargs)


    def getJPackages(self, **args):
        nid = args.get('nid')
        domain = args.get('domain', None)

        return self.execute('jpackage_list', nid=nid, domain=domain)

    def getJPackageInfo(self, **args):
        nid = args.get('nid')
        domain = args.get('domain', None)
        name = args.get('pname', None)
        version = args.get('version', None)
        return self.execute('jpackage_info', nid=nid, domain=domain, pname=name, version=version)

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
        domain = args.get('domain', None)
        name = args.get('pname', None)
        version = args.get('version', None)
        return self.execute('jpackage_fileinfo', nid=nid, domain=domain, pname=name, version=version)

    def action(self, **args):
        nid = args.get('nid')
        domain = args.get('domain', None)
        name = args.get('pname', None)
        action = args.get('action', None)
        version = args.get('version', None)
        return self.execute('jpackage_action', nid=nid, domain=domain, pname=name, version=version, action=action)

