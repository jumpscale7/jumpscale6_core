from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.grid.osis
import JumpScale.lib.diskmanager

class GridHealthChecker(object):

    def __init__(self):
        self.client = j.clients.agentcontroller.get()
        self.osiscl = j.core.osis.getClient(user='root')
        self.heartbeatcl = j.core.osis.getClientForCategory(self.osiscl, 'system', 'heartbeat')

    def checkElasticSearch(self):
        nid = j.application.whoAmI.nid
        result = self.client.executeJumpScript('jumpscale', 'check_elasticsearch', nid=nid)['result']
        return result

    def checkRedis(self, nid):
        result = self.client.executeJumpScript('jumpscale', 'check_redis', nid=nid)['result']
        return result

    def checkWorkers(self, nid):
        result = self.client.executeJumpScript('jumpscale', 'workerstatus', nid=nid)['result'] 
        return result

    def checkProcessManagers(self, nid):
        self.client.executeJumpScript('jumpscale', 'heartbeat', nid=nid, timeout=10)
        gid = j.application.whoAmI.gid
        if self.heartbeatcl.exists('%s_%s' % (gid, nid)):
            heartbeat = self.heartbeatcl.get('%s_%s' % (gid, nid))
            lastchecked = heartbeat.lastcheck

            if  j.base.time.getEpochAgo('-2m') < lastchecked:
                return True
        return False

    def checkDisks(self, nid):
        result = dict()
        disks = j.system.platform.diskmanager.partitionsFind(mounted=True)
        for disk in disks:
            if (disk.free and disk.size) and (disk.free / float(disk.size)) * 100 < 10:
                result[disk.path] = 'FREE SPACE LESS THAN 10%'
            else:
                result[disk.path] = '%.2f GB free space available' % (disk.free/1024.0)
        return result

    def gatherNodeChecks(self, nid):
        result = self.client.executeJumpScript('jumpscale', 'healthchecker_gathering', nid=nid, timeout=10)
        return result