from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.grid.osis
import JumpScale.lib.diskmanager

class GridHealthChecker(object):

    def __init__(self):
        self.client = j.clients.agentcontroller.get()
        self.osiscl = j.core.osis.getClient(user='root')
        self.heartbeatcl = j.core.osis.getClientForCategory(self.osiscl, 'system', 'heartbeat')
        self.nids=[]
        self.errors=[]
        self.status=[]
        self.tostdout=False

    def _clean(self):
        self.nids=[]
        self.errors=[]
        self.status=[]


    def runAll(self):
        #do all tests
        self._clean()
        self.getNodes()
        pass

    def _addError(self,nid,msg,category):
        if self.tostdout:
            print ""
        self.errors.append((nid,msg,category))

    def _addResult(self,nid,msg,category):
        if self.tostdout:
            print ""        
        self.status.append((nid,msg,category))


    def getNodes(self):        
        """
        cache in mem
        list nodes from grid
        list nodes from heartbeat
        if gridnodes found not in heartbeat -> error
        if heartbeat nodes found not in gridnodes -> error
        all the ones found in self.nids (return if populated)
        """
        pass

    def checkElasticSearch(self,clean=True):
        if clean:
            self._clean()

        raise RuntimeError("lookup master, this nid you need")
        nid = j.application.whoAmI.nid
        result = self.client.executeJumpScript('jumpscale', 'check_elasticsearch', nid=nid)['result']
        return result

    def checkRedisAllNodes(self,clean=True):
        if clean:
            self._clean()

        pass

    def checkRedis(self, nid,clean=True):
        if clean:
            self._clean()

        result = self.client.executeJumpScript('jumpscale', 'check_redis', nid=nid)['result']
        return result

    def checkWorkersAllNodes(self,clean=True):
        if clean:
            self._clean()

        pass

    def checkWorkers(self, nid,clean=True):
        if clean:
            self._clean()

        result = self.client.executeJumpScript('jumpscale', 'workerstatus', nid=nid)['result'] 
        return result

    def checkProcessManagerAllNodes(self,clean=True):
        if clean:
            self._clean()

        raise RuntimeError("walk over known nodes (2 find queries for known nodes & hartbeat")
        #osis work only
        #use from overview macro

    def checkProcessManager(self, nid,clean=True):
        """
        execute heartbeat on specified node and see if result came in osis
        """
        if clean:
            self._clean()

        gid = j.application.whoAmI.gid
        if self.heartbeatcl.exists('%s_%s' % (gid, nid)):
            heartbeat = self.heartbeatcl.get('%s_%s' % (gid, nid))
            lastchecked = heartbeat.lastcheck
            if  j.base.time.getEpochAgo('-2m') < lastchecked:
                return True
        return False

    def checkDisksAllNodes(self,clean=True):
        if clean:
            self._clean()

        raise RuntimeError("not impl")

    def checkDisks(self, nid,clean=True):
        raise RuntimeError("needs to be nid,checkDisks, use jumpscript")
        if clean:
            self._clean()
        result = dict()
        disks = j.system.platform.diskmanager.partitionsFind(mounted=True)
        for disk in disks:
            if (disk.free and disk.size) and (disk.free / float(disk.size)) * 100 < 10:
                result[disk.path] = 'FREE SPACE LESS THAN 10%'
            else:
                result[disk.path] = '%.2f GB free space available' % (disk.free/1024.0)
        return result

    # def gatherNodeChecks(self, nid):
    #     result = self.client.executeJumpScript('jumpscale', 'healthchecker_gathering', nid=nid, timeout=10)
    #     return result