from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.grid.osis

class GridHealthChecker(object):

    def __init__(self):
        self.client = j.clients.agentcontroller.get()

    def _getNodesIds(self):
        result = list()
        osiscl = j.core.osis.getClient(user='root')
        nodecl = j.core.osis.getClientForCategory(osiscl, 'system', 'node')
        nodes = nodecl.list()
        for node in nodes:
            nobj = nodecl.get(node)
            result.append(nobj.id)
        return result

    def checkElasticSearch(self):
        nid = j.application.whoAmI.nid
        result = self.client.executeJumpScript('jumpscale', 'check_elasticsearch', nid=nid)['result']
        return result

    def checkRedis(self):
        nodes = self._getNodesIds()
        result = dict()
        for nid in nodes:
            result[nid] = self.client.executeJumpScript('jumpscale', 'check_redis', nid=nid)['result']
        return result

    def checkWorkers(self):
        nodes = self._getNodesIds()
        result = dict()
        for nid in nodes:
            result[nid] = self.client.executeJumpScript('jumpscale', 'workerstatus', nid=nid)['result']
        return result

    def checkProcessManagers(self):
        nodes = self._getNodesIds()
        result = dict()
        for nid in nodes:
            response = self.client.executeJumpScript('jumpscale', 'echo_sync', args={'msg': 'ping'}, nid=nid, timeout=10)['result']
            result[nid] = True if response else False
        return result