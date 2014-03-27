from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.grid.osis
import JumpScale.baselib.units

class GridHealthChecker(object):

    def __init__(self):
        self._client = j.clients.agentcontroller.get()
        self._osiscl = j.core.osis.getClient(user='root')
        self._heartbeatcl = j.core.osis.getClientForCategory(self._osiscl, 'system', 'heartbeat')
        self._nodecl = j.core.osis.getClientForCategory(self._osiscl, 'system', 'node')
        self._runningnids = list()
        self._nids = list()
        self._errors = dict()
        self._status = dict()
        self._tostdout = False
        self.getNodes()

    def _clean(self):
        self._errors = dict()
        self._status = dict()

    def _addError(self, nid, result, category):
        if self._tostdout:
            print "*ERROR*: %s on node %s. Details: %s" % (category, nid, result)
        self._errors.setdefault(nid, {})
        self._errors[nid].update({category:{}})
        self._errors[nid][category].update(result)

    def _addResult(self, nid, result, category):
        if self._tostdout:
            print "*OK*   : %s on node %s. Details: %s" % (category, nid, result)
        self._status.setdefault(nid, {})
        self._status[nid].setdefault(category, {})
        self._status[nid][category].update(result)

    def _checkRunningNIDs(self):
        self._runningnids = list()

        heartbeats = self._heartbeatcl.simpleSearch({})
        for heartbeat in heartbeats:
            if heartbeat['nid'] not in self._nids:
                self.getNodes()
                break

        nid2hb = dict([(x['nid'], x['lastcheck']) for x in heartbeats])
        for nid in self._nids:
            lastchecked = nid2hb[nid]
            if nid in nid2hb.keys() and j.base.time.getEpochAgo('-2m') < lastchecked:
                self._runningnids.append(nid)

    def toStdout(self):
        self._tostdout = True

    def getNodes(self):        
        """
        cache in mem
        list nodes from grid
        list nodes from heartbeat
        if gridnodes found not in heartbeat -> error
        if heartbeat nodes found not in gridnodes -> error
        all the ones found in self._nids (return if populated)
        """
        nodes = self._nodecl.simpleSearch({})
        self._nids = [node['id'] for node in nodes]
        gridmasterip = j.application.config.get('grid.master.ip')
        if gridmasterip == '127.0.0.1':
            self.masternid = j.application.whoAmI.nid
        else:
            for node in nodes:
                if gridmasterip in node['ipaddr']:
                    self.masternid = node['id'] 
                    break
        self._checkRunningNIDs()

    def runAll(self):
        self._clean()
        self.getNodes()
        self.checkProcessManagerAllNodes(clean=False)
        if self._runningnids:
            self.checkElasticSearch(clean=False)
            self.checkRedisAllNodes(clean=False)
            self.checkWorkersAllNodes(clean=False)
            self.checkDisksAllNodes(clean=False)
        return self._status, self._errors

    def checkElasticSearch(self, clean=True):
        if clean:
            self._clean()
        eshealth = self._client.executeJumpScript('jumpscale', 'info_gather_elasticsearch', nid=self.masternid)['result']
        size, unit = j.tools.units.bytes.converToBestUnit(eshealth['size'])
        eshealth['size'] = '%s %sB' % (size, unit)
        size, unit = j.tools.units.bytes.converToBestUnit(eshealth['memory_usage'])
        eshealth['memory_usage'] = '%s %sB' % (size, unit)

        if eshealth['health']['status'] in ['red']:
            self._addError(self.masternid, eshealth, 'elasticsearch')
        else:
            self._addResult(self.masternid, eshealth, 'elasticsearch')
        if clean:
            return self._status, self._errors

    def checkRedisAllNodes(self, clean=True):
        if clean:
            self._clean()
        for nid in self._runningnids:
            self.checkRedis(nid, clean=False)
        if clean:
            return self._status, self._errors

    def checkRedis(self, nid, clean=True):
        if clean:
            self._clean()
        redis = self._client.executeJumpScript('jumpscale', 'info_gather_redis', nid=nid)['result']
        for port, result in redis.iteritems():
            size, unit = j.tools.units.bytes.converToBestUnit(result['memory_usage'])
            result['memory_usage'] = '%s %sB' % (size, unit)
            if result['alive']:
                self._addResult(nid, {port: result}, 'redis')
            else:
                self._addError(nid, {port: result}, 'redis')
        if clean:
            return self._status, self._errors

    def checkWorkersAllNodes(self,clean=True):
        if clean:
            self._clean()
        for nid in self._runningnids:
            self.checkWorkers(nid, clean=False)
        if clean:
            return self._status, self._errors

    def checkWorkers(self, nid, clean=True):
        if clean:
            self._clean()
        workers = self._client.executeJumpScript('jumpscale', 'workerstatus', nid=nid)['result']
        for worker, stats in workers.iteritems():
            size, unit = j.tools.units.bytes.converToBestUnit(stats['mem'])
            stats['mem'] = '%s %sB' % (size, unit)
            if stats['status']:
                self._addResult(nid, {worker: stats}, 'workers')
            else:
                self._addError(nid, {worker: stats}, 'workers')
        if clean:
            return self._status, self._errors


    def checkProcessManagerAllNodes(self, clean=True):
        if clean:
            self._clean()
        self._checkRunningNIDs()

        haltednodes = set(self._nids)-set(self._runningnids)
        for nid in haltednodes:
            self._addError(nid, {nid: False}, 'processmanager')
        for nid in self._runningnids:
            self._addResult(nid, {nid: True}, 'processmanager')
        if clean:
            return self._status, self._errors

    def checkProcessManager(self, nid, clean=True):
        """
        Check heartbeat on specified node, see if result came in osis
        """
        if clean:
            self._clean()
        gid = j.application.whoAmI.gid
        if self._heartbeatcl.exists('%s_%s' % (gid, nid)):
            heartbeat = self._heartbeatcl.get('%s_%s' % (gid, nid))
            lastchecked = heartbeat.lastcheck
            if  j.base.time.getEpochAgo('-2m') < lastchecked:
                self._addResult(nid, {nid: True}, 'processmanager')
            else:
                self._addError(nid, {nid: False}, 'processmanager')
        else:
            self._addError(nid, {nid: False}, 'processmanager')
        if clean:
            return self._status, self._errors

    def checkDisksAllNodes(self, clean=True):
        if clean:
            self._clean()
        for nid in self._runningnids:
            self.checkDisks(nid, clean=False)
        if clean:
            return self._status, self._errors

    def checkDisks(self, nid, clean=True):
        if clean:
            self._clean()
        disks = self._client.executeJumpScript('jumpscale', 'check_disks', nid=nid)['result']
        for path, disk in disks.iteritems():
            if (disk['free'] and disk['size']) and (disk['free'] / float(disk['size'])) * 100 < 10:
                disk['message'] = 'FREE SPACE LESS THAN 10%% on disk %s' % path
                disk['status'] = False
                self._addError(nid, {path: disk}, 'disks')
            else:
                if disk['free']:
                    size, unit = j.tools.units.bytes.converToBestUnit(disk['free'], 'M')
                    disk['message'] = '%.2f %siB free space available' % (size, unit)

                else:
                    disk['message'] = 'Disk is not mounted, Info is not available'
                disk['status'] = True
                self._addResult(nid, {path: disk}, 'disks')
        if clean:
            return self._status, self._errors

    def checkStatusAllNodes(self, clean=True):
        if clean:
            self._clean()
        for nid in self._runningnids:
            self.checkStatus(nid, clean=False)
        if clean:
            return self._status, self._errors

    def checkStatus(self, nid, clean=True):
        if clean:
            self._clean()
        stats = self._client.executeJumpScript('jumpscale', 'info_gather_healthcheck_results', nid=nid)['result']

        health = True
        for check, state in stats.iteritems():
            if state == False:
                health = False
        stats['health'] = health
        self._addResult(nid, stats, 'healthcheck')
        if clean:
            return self._status, self._errors