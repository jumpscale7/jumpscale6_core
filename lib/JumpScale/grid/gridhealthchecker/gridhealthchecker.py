from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.grid.osis
import JumpScale.baselib.units
import gevent

class GridHealthChecker(object):

    def __init__(self):
        print "get agentcontroller client: ",
        self._client = j.clients.agentcontroller.get()
        print "OK"
        print "get osis client: ",
        self._osiscl = j.core.osis.getClient(user='root')
        print "OK"
        print "get osis client for heartbeat: ",
        self._heartbeatcl = j.core.osis.getClientForCategory(self._osiscl, 'system', 'heartbeat')
        print "OK"
        print "get osis client for system:node: ",
        self._nodecl = j.core.osis.getClientForCategory(self._osiscl, 'system', 'node')
        print "OK"
        self._runningnids = list()
        self._nids = list()
        self._nodenames = dict()
        self._errors = dict()
        self._status = dict()
        self._tostdout = True
        self.masternid = 0
        with j.logger.nostdout():
            self.getNodes()

    def _clean(self):
        self._errors = dict()
        self._status = dict()

    def _addError(self, nid, result, category=""):
        self._errors.setdefault(nid, {})
        self._errors[nid].update({category:list()})
        if isinstance(result, basestring):
            print '\t           %s' % result
            self._errors[nid][category].append({'errormessage': result})
        else:
            self._errors[nid][category].append(result)

    def _addResult(self, nid, result, category):
        self._status.setdefault(nid, {})
        self._status[nid].setdefault(category, list())
        self._status[nid][category].append(result)

    def _parallelize(self, functionname, clean=False, category=""):
        if functionname.func_name in ['ping']:
            nodes = self._nids
        else:
            nodes = self._runningnids
        greens = list()
        for nid in nodes:
            greenlet = gevent.Greenlet(functionname, nid, clean)
            greenlet.nid = nid
            greenlet.start()
            greens.append(greenlet)
        gevent.joinall(greens)
        for green in greens:
            result = green.value
            if result:
                results, errors = green.value
            else:
                results = list()
                errors = [(green.nid, {'message': str(green.exception), 'state': 'UNKOWN'}, category)]

            self._returnResults(results, errors)

    def _returnResults(self, results, errors):
        for nid, result, category in results:
            self._addResult(nid, result, category)
        for nid, result, category in errors:
            self._addError(nid, result, category)
        return self._status, self._errors

    def _checkRunningNIDs(self):
        print '\nCHECK HEARTBEATS'
        self._runningnids = list()
        print "get all heartbeats (just query from ES):",
        heartbeats = self._heartbeatcl.simpleSearch({})
        print "OK"
        for heartbeat in heartbeats:
            if heartbeat['nid'] not in self._nids and  heartbeat['nid']  not in self._nidsNonActive:
                self._addError(heartbeat['nid'],"found heartbeat node '%s' which is not in grid nodes."%(heartbeat['nid']),"heartbeat")

        nid2hb = dict([(x['nid'], x['lastcheck']) for x in heartbeats])
        print "check heartbeats for all nodes"
        for nid in self._nids:
            if nid not in self._nidsNonActive:
                if nid in nid2hb:
                    lastchecked = nid2hb[nid]
                    if j.base.time.getEpochAgo('-2m') < lastchecked:
                        # print "%s"%nid,
                        self._runningnids.append(nid)
                    else:                        
                        hago= round(float(j.base.time.getTimeEpoch()-lastchecked)/3600,1)
                        name=self._nodenames[nid]
                        self._addError(nid,"On node:'%s' (%s). Processmanager is not responding, last heartbeat %s hours ago"%(name,nid,hago),"heartbeat")    
                else:
                    self._addError(nid,"found heartbeat node '%s' which is not in grid nodes." % (nid),"heartbeat")

    def _checkRunningNIDsFromPing(self):
        self._runningnids = self._nids[:]
        for nid, error in self._errors.iteritems():
            for category in error:
                if category == 'processmanagerping':
                    self._runningnids.remove(nid)

    def toStdout(self):
        self._tostdout = True

    def getNodes(self, pprint=False):        
        """
        cache in mem
        list nodes from grid
        list nodes from heartbeat
        if gridnodes found not in heartbeat -> error
        if heartbeat nodes found not in gridnodes -> error
        all the ones found in self._nids (return if populated)
        """
        nodes = self._nodecl.simpleSearch({})
        self._nids = []
        self._nidsNonActive=[]
        gridmasterip = j.application.config.get('grid.master.ip')
        for node in nodes:
            if node["active"]==True:
                self._nids.append(node['id'])
            else:
                self._nidsNonActive.append(node['id'])
        
        nodes=[node for node in nodes if node["active"]==True]

        for node in nodes:
            self._nodenames[node['id']] = node['name']
            if gridmasterip in node['ipaddr']:
                self.masternid = node['id'] 
        if gridmasterip == '127.0.0.1':
            self.masternid = j.application.whoAmI.nid
        self.pingAllNodesSync(clean=True, pprint=pprint)
        self._checkRunningNIDsFromPing()

    def runAll(self):
        self._clean()
        self.getNodes(pprint=True)
        self._clean()
        print
        self.checkHeartbeatsAllNodes(clean=False)
        self.checkProcessManagerAllNodes(clean=False)
        print '\n**Running tests on %s node(s). %s node(s) have not responded to ping**\n' % (len(self._runningnids), len(self._nids)-len(self._runningnids))
        if self._runningnids:
            self.pingAllNodesAsync(clean=False)
            self.checkElasticSearch(clean=False)
            self.checkRedisAllNodes(clean=False)
            self.checkWorkersAllNodes(clean=False)
            self.checkDisksAllNodes(clean=False)
        return self._status, self._errors

    def printStatus(self, category):
        if self._errors:
            errors = False
            for nid, categories in self._errors.iteritems():
                if category in categories:
                    errors = True
                    print "\t**ERROR**: %s test failed on node '%s' id:'%s'" % (category.title(), self._nodenames.get(nid, 'N/A'), nid)
            if not errors:
                print '\t**OK**'

    def checkElasticSearch(self, clean=True):
        if self._nids==[]:
            self.getNodes()
        print "CHECK ELASTICSEARCH"
        if clean:
            self._clean()

        if self.masternid not in self._runningnids:
            self._addError(self.masternid, {'state': 'UNKOWN'}, 'elasticsearch')
        else:
            eshealth = self._client.executeJumpScript('jumpscale', 'info_gather_elasticsearch', nid=self.masternid, timeout=5)
            if eshealth['state'] == 'TIMEOUT':
                self._addError(self.masternid, {'state': 'TIMEOUT'}, 'elasticsearch')
            elif eshealth['state'] != 'OK':
                self._addError(self.masternid, {'state': 'UNKOWN'}, 'elasticsearch')
            else:
                eshealth = eshealth['result']
                if eshealth==None:
                    self._addError(self.masternid,"elasticsearch did not return info for healthcheck","elasticsearch")
                    return self._status, self._errors
                size, unit = j.tools.units.bytes.converToBestUnit(eshealth['size'])
                eshealth['size'] = '%.2f %sB' % (size, unit)
                size, unit = j.tools.units.bytes.converToBestUnit(eshealth['memory_usage'])
                eshealth['memory_usage'] = '%.2f %sB' % (size, unit)

                if eshealth['health']['status'] in ['red']:
                    self._addError(self.masternid, eshealth, 'elasticsearch')
                else:
                    self._addResult(self.masternid, eshealth, 'elasticsearch')

        if self._tostdout:
            self.printStatus('elasticsearch')
        if clean:
            return self._status, self._errors

    def checkRedisAllNodes(self, clean=True):
        if self._nids==[]:
            self.getNodes()

        print "CHECK REDIS ON %s NODE(S)" % len(self._runningnids)
        if clean:
            self._clean()
        self._parallelize(self.checkRedis, False, 'redis')
        if self._tostdout:
            self.printStatus('redis')
        if clean:
            return self._status, self._errors

    def getWikiStatus(self, status):
        colormap = {'RUNNING': 'green', 'HALTED': 'red', 'UNKOWN': 'orange',
                    'BROKEN': 'red', 'OK': 'green', 'NOT OK': 'red'}
        return '{color:%s}*%s*{color}' % (colormap.get(status, 'orange'), status)

    def checkRedis(self, nid, clean=True):
        if self._nids==[]:
            self.getNodes()

        if clean:
            self._clean()

        results = list()
        errors = list()
        result = self._client.executeJumpScript('jumpscale', 'info_gather_redis', nid=nid, timeout=5)
        redis = result['result']
        if result['state'] != 'OK' or not redis:
            errors.append((nid, {'state': 'UNKOWN'}, 'redis'))
            redis = dict()

        for port, result in redis.iteritems():
            size, unit = j.tools.units.bytes.converToBestUnit(result['memory_usage'])
            result['memory_usage'] = '%.2f %sB' % (size, unit)
            result['port'] = port
            if result['state'] == 'RUNNING':
                results.append((nid, result, 'redis'))
            else:
                errors.append((nid, result, 'redis'))
        if clean:
            return self._returnResults(results, errors)
        return results, errors

    def checkWorkersAllNodes(self,clean=True):
        if self._nids==[]:
            self.getNodes()

        if clean:
            self._clean()
        print "CHECK WORKERS ON %s NODE(S)" % len(self._runningnids)
        self._parallelize(self.checkWorkers, False, 'workers')
        if self._tostdout:
            self.printStatus('workers')
        if clean:
            return self._status, self._errors

    def checkWorkers(self, nid, clean=True):
        if self._nids==[]:
            self.getNodes()

        if clean:
            self._clean()
        results = list()
        errors = list()
        result = self._client.executeJumpScript('jumpscale', 'workerstatus', nid=nid, timeout=30)
        workers = result['result']
        if result['state'] != 'OK' or not workers:
            errors.append((nid, {'state':'UNKOWN', 'mem': '0 B'}, 'workers'))
            workers = dict()
        for worker, stats in workers.iteritems():
            size, unit = j.tools.units.bytes.converToBestUnit(stats['mem'])
            stats['mem'] = '%.2f %sB' % (size, unit)
            stats['name'] = worker
            if stats['state'] == 'RUNNING':
                results.append((nid, stats, 'workers'))
            else:
                errors.append((nid, stats, 'workers'))
        if clean:
            return self._returnResults(results, errors)
        return results, errors


    def checkProcessManagerAllNodes(self, clean=True):
        if clean:
            self._clean()
        if self._nids==[]:
            self.getNodes()
        print "CHECK PROCESSMANAGERS"
        haltednodes = set(self._nids)-set(self._runningnids)
        for nid in haltednodes:
            self._addError(nid, {'state': 'HALTED'}, 'processmanager')
        for nid in self._runningnids:
            self._addResult(nid, {'state': 'RUNNING'}, 'processmanager')
        if self._tostdout:
            self.printStatus('processmanager')
        if clean:
            return self._status, self._errors


    def checkHeartbeatsAllNodes(self, clean=True):
        if clean:
            self._clean()
        if self._nids==[]:
            self.getNodes()
        print 'CHECK HEARTBEATS'
        print "get all heartbeats (just query from ES):",
        print "OK"
        heartbeats = self._heartbeatcl.simpleSearch({})
        for heartbeat in heartbeats:
            if heartbeat['nid'] not in self._nids and  heartbeat['nid']  not in self._nidsNonActive:
                self._addError(heartbeat['nid'],"found heartbeat node '%s' which is not in grid nodes."%(heartbeat['nid']),"heartbeat")

        nid2hb = dict([(x['nid'], x['lastcheck']) for x in heartbeats])
        print "check heartbeats for all nodes"
        for nid in self._nids:
            if nid not in self._nidsNonActive:
                if nid in nid2hb:
                    lastchecked = nid2hb[nid]
                    if not j.base.time.getEpochAgo('-2m') < lastchecked:
                        hago= round(float(j.base.time.getTimeEpoch()-lastchecked)/3600,1)
                        name=self._nodenames[nid]
                        self._addError(nid,"On node:'%s' (%s). Processmanager is not responding, last heartbeat %s hours ago"%(name,nid,hago),"heartbeat")    
                else:
                    self._addError(nid,"found heartbeat node '%s' which is not in grid nodes." % (nid),"heartbeat")
        if clean:
            return self._status, self._errors

    def checkProcessManager(self, nid, clean=True):
        """
        Check heartbeat on specified node, see if result came in osis
        """
        if clean:
            self._clean()
        if self._nids==[]:
            self.getNodes()

        gid = j.application.whoAmI.gid
        if self._heartbeatcl.exists('%s_%s' % (gid, nid)):
            heartbeat = self._heartbeatcl.get('%s_%s' % (gid, nid))
            lastchecked = heartbeat.lastcheck
            if  j.base.time.getEpochAgo('-2m') < lastchecked:
                self._addResult(nid, {'state': 'RUNNING'}, 'processmanager')
            else:
                self._addError(nid, {'state': 'HALTED'}, 'processmanager')
        else:
            self._addError(nid, {'state': 'UNKOWN'}, 'processmanager')
        if clean:
            return self._status, self._errors

    def checkDisksAllNodes(self, clean=True):
        if clean:
            self._clean()
        if self._nids==[]:
            self.getNodes()
        print "CHECK DISKS ON %s NODE(S)" % len(self._runningnids)
        self._parallelize(self.checkDisks, False, 'disks')
        if self._tostdout:
            self.printStatus('disks')
        if clean:
            return self._status, self._errors

    def pingAllNodesSync(self, clean=True, pprint=False):
        if clean:
            self._clean()
        if self._nids==[]:
            self.getNodes()
        if pprint:
            print "PROCESS MANAGER PING TO ALL (%s) NODES" % len(self._nids)
        self._parallelize(self.ping, False, 'processmanagerping')
        if self._tostdout:
            self.printStatus('processmanagerping')
        if clean:
            return self._status, self._errors

    def pingAllNodesAsync(self, clean=True):
        print "WORKER PING TO %s NODE(S)" % len(self._runningnids)
        self._parallelize(self.pingasync, False, 'workerping')
        if self._tostdout:
            self.printStatus('workerping')
        if clean:
            return self._status, self._errors        

    def ping(self,nid,clean=True):
        results = list()
        errors = list()
        result = self._client.executeJumpScript('jumpscale', 'echo_sync', args={"msg":"ping"},nid=nid, timeout=5)
        if not result["result"]=="ping":
            errors.append((nid, {'ping': 'down'}, 'processmanagerping'))
        return results, errors

    def pingasync(self,nid,clean=True):
        results = list()
        errors = list()
        result = self._client.executeJumpScript('jumpscale', 'echo_async', args={"msg":"ping"}, nid=nid, timeout=5)
        if not result["result"]=="ping":
            errors.append((nid, {'ping': 'down'}, 'workerping'))
        return results, errors

    def checkDisks(self, nid, clean=True):
        if self._nids==[]:
            self.getNodes()

        if clean:
            self._clean()
        results = list()
        errors = list()
        result = self._client.executeJumpScript('jumpscale', 'check_disks', nid=nid, timeout=30)
        disks = result['result']
        if result['state'] != 'OK':
            errors.append((nid, {'state': 'UNKOWN'}, 'disks'))
            disks = dict()
        for path, disk in disks.iteritems():
            disk['path'] = path
            if (disk['free'] and disk['size']) and (disk['free'] / float(disk['size'])) * 100 < 10:
                disk['message'] = 'FREE SPACE LESS THAN 10%% on disk %s' % path
                disk['state'] = 'NOT OK'
                errors.append((nid, {path: disk}, 'disks'))
            else:
                if disk['free']:
                    size, unit = j.tools.units.bytes.converToBestUnit(disk['free'], 'M')
                    disk['message'] = '%.2f %siB free space available' % (size, unit)

                else:
                    disk['message'] = 'Disk is not mounted, Info is not available'
                disk['state'] = 'OK'
                results.append((nid, disk, 'disks'))
        if clean:
            return self._returnResults(results, errors)
        return results, errors
