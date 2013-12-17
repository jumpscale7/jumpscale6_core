from JumpScale import j
import JumpScale.grid.geventws
import JumpScale.grid.osis
import JumpScale.grid.agentcontroller
import requests

def mbToKB(value):
    if not value:
        return value
    return value * 1024

class system_gridmanager(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        self._te={}
        self.actorname="gridmanager"
        self.appname="system"
        self.clients={}
        self._nodeMap = dict()
        self.clientsIp = dict()

        self.passwd = j.application.config.get("system.superadmin.passwd")

        osis = j.core.osis.getClient(j.application.config.get("grid.master.ip"), passwd=self.passwd)
        self.osis_node = j.core.osis.getClientForCategory(osis,"system","node")
        self.osis_job = j.core.osis.getClientForCategory(osis,"system","job")
        self.osis_eco = j.core.osis.getClientForCategory(osis,"system","eco")
        self.osis_process = j.core.osis.getClientForCategory(osis,"system","process")
        self.osis_application = j.core.osis.getClientForCategory(osis,"system","applicationtype")
        self.osis_grid = j.core.osis.getClientForCategory(osis,"system","grid")
        self.osis_machine = j.core.osis.getClientForCategory(osis,"system","machine")
        self.osis_disk = j.core.osis.getClientForCategory(osis,"system","disk")
        self.osis_vdisk = j.core.osis.getClientForCategory(osis,"system","vdisk")
        self.osis_alert = j.core.osis.getClientForCategory(osis,"system","alert")
        self.osis_log = j.core.osis.getClientForCategory(osis,"logger","log")

    def getClient(self,nid):
        nid = int(nid)
        if nid not in self.clients:
            if nid not in self._nodeMap:
                self.getNodes()
            if nid not in self._nodeMap:
                raise RuntimeError('Could not get client for node %s!' % nid)
            for ip in self._nodeMap[nid]['ipaddr']:
                if j.system.net.tcpPortConnectionTest(ip, 4445):
                    self.clients[nid] = j.servers.geventws.getClient(ip, 4445, org="myorg", user="admin", passwd="1234",category="processmanager")
                    self.clientsIp[nid] = ip
                    return self.clients[nid]
            raise RuntimeError('Could not get client for node %s!' % nid)

        return self.clients[nid]

    def getNodeSystemStats(self, nodeId, **kwargs):
        """
        ask the right processmanager on right node to get the information about node system
        param:nodeId id of node
        result json
        """
        client=self.getClient(nodeId)
        return client.monitorSystem()

    def _getNode(self, nid):
        node=self.osis_node.get(nid)
        r = dict()
        r["id"]=node.id
        r["roles"]=node.roles
        r["name"]=node.name
        r["ipaddr"]=node.ipaddr
        self._nodeMap[node.id] = r
        return r

    def getNodes(self, gid=None, name=None, roles=None, ipaddr=None, macaddr=None, id=None, **kwargs):
        """
        list found nodes
        result list(list)
        """
        params = {'gid': gid,
                  'name': name,
                  'id': id,
                  }
        results = self.osis_node.simpleSearch(params)
        def myfilter(node):
            self._nodeMap[node['id']] = node
            if roles and not set(roles).issubset(set(node['roles'])):
                return False
            if ipaddr and ipaddr not in node['ipaddr']:
                return False
            if macaddr and macaddr not in node['netaddr']:
                return False
            return True

        return filter(myfilter, results)


    def getProcessStats(self, nodeId, domain="", name="", **kwargs):
        """
        ask the right processmanager on right node to get the information
        param:nodeId id of node
        param:domain optional domain name for process
        param:name optional name for process
        result json
        """
        if domain=="*":
            domain=""
        if name=="*":
            name=""
        client=self.getClient(nodeId)
        return client.monitorProcess(domain=domain,name=name)

    def getStatImage(self,statKey,width=500,height=250, **kwargs):
        """
        @param statkey e.g. n1.disk.mbytes.read.sda1.last
        """
        statKey=statKey.strip()
        if statKey[0]=="n":
            #node info
            nodeId=int(statKey.split(".")[0].replace("n",""))
        else:
            raise RuntimeError("Could not parse statKey, only node stats supported for now (means starting with n)")

        client=self.getClient(nodeId)
        ip=self.clientsIp[nodeId] 

        url="http://%s:8081/render/?width=%s&height=%s&target=%s&lineWidth=2&graphOnly=false&hideAxes=false&hideGrid=false&areaMode=first&tz=CET"%(ip,width,height,statKey)

        r = requests.get(url)

        return r.content

    def getProcessesActive(self, nodeId, name, domain, **kwargs):
        """
        ask the right processmanager on right node to get the info (this comes not from osis)
        output all relevant info (no stat info for that we have getProcessStats)
        param:nodeId id of node (if not specified goes to all nodes and aggregates)
        param:name optional name for process name (part of process name)
        param:domain optional name for process domain (part of process domain)
        result json
        """
        client = self.getClient(nodeId)
        return client.getProcessesActive(domain, name)

    def getJob(self, id, includeloginfo, includechildren, **kwargs):
        """
        gets relevant info of job (also logs)
        can be used toreal time return job info
        param:id obliged id of job
        param:includeloginfo if true fetch all logs of job & return as well
        param:includechildren if true look for jobs which are children & return that info as well
        """
        job = self.osis_job.get(id)
        return {'result': job}

    def getLogs(self, id, level, category, text, from_, to, jid, nid, gid, pid, tags, **kwargs):
        """
        interface to get log information
        param:id only find 1 log entry
        param:level level between 1 & 9; all levels underneath are found e.g. level 9 means all levels
        param:category match on multiple categories; are comma separated
        param:text match on text in body
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs to date specified
        param:jid find logs for specified jobid
        param:nid find logs for specified node
        param:gid find logs for specified grid
        param:pid find logs for specified process (on grid level)
        param:tags comma separted list of tags/labels
        """
        from_ = self._getEpoch(from_)
        to = self._getEpoch(to)
        params = {'id': id,
                  'level': {'name': 'level', 'value': level, 'eq': 'lte'},
                  'category': category,
                  'text': text,
                  'from_': {'name': 'epoch', 'value': from_, 'eq': 'gte'},
                  'to': {'name': 'epoch', 'value': to, 'eq': 'lte'},
                  'jid': jid,
                  'nid': nid,
                  'gid': gid,
                  'pid': pid,
                  'tags': tags,
                  }
        return self.osis_log.simpleSearch(params)

    def getJobs(self, id, from_, to, nid, gid, parent, roles, state, jsorganization, jsname, **kwargs):
        """
        interface to get job information
        param:id only find 1 job entry
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs to date specified
        param:nid find jobs for specified node
        param:gid find jobs for specified grid
        param:parent find jobs which are children of specified parent
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:state OK;ERROR;...
        param:jsorganization
        param:jsname
        """
        from_ = self._getEpoch(from_)
        to = self._getEpoch(to)
        params = {'ffrom': {'name': 'timeStart', 'value': from_, 'eq': 'gte'},
                  'to': {'name': 'timeStart', 'value': to, 'eq': 'lte'},
                  'nid': nid,
                  'gid': gid,
                  'id': id,
                  'parent': parent,
                  'state': state,
                  'jsorganization': jsorganization,
                  'jsname': jsname}

        return self.osis_job.simpleSearch(params)

    def getErrorconditions(self, id, level, descr, descrpub, from_, to, nid, gid, category, tags, type, jid, jidparent, jsorganization, jsname, **kwargs):
        """
        interface to get errorcondition information (eco)
        param:id only find 1 eco entry
        param:level level between 1 & 3; all levels underneath are found e.g. level 3 means all levels
        param:descr match on text in descr
        param:descrpub match on text in descrpub
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos to date specified
        param:nid find ecos for specified node
        param:gid find ecos for specified grid
        param:category match on multiple categories; are comma separated
        param:tags comma separted list of tags/labels
        param:type
        param:jid find ecos for specified job
        param:jidparent find ecos which are children of specified parent job
        param:jsorganization find ecos coming from scripts from this org
        param:jsname find ecos coming from scripts with this name
        """
        from_ = self._getEpoch(from_)
        to = self._getEpoch(to)
        params = {'ffrom': {'name': 'epoch', 'value': from_, 'eq': 'gte'},
                  'to': {'name':'epoch','value': to, 'eq': 'lte'},
                  'nid': nid,
                  'level': level,
                  'descr': descr,
                  'descrpub': descrpub,
                  'category': category,
                  'tags': tags,
                  'type': type,
                  'gid': gid,
                  'jid': jid,
                  'jidparent': jidparent,
                  'id': id,
                  'jsorganization': jsorganization,
                  'jsname': jsname}
        return self.osis_eco.simpleSearch(params)


    def getProcesses(self, id, name, nid, gid, aid, from_, to, **kwargs):
        """
        list processes (comes from osis), are the grid unique processes (not integrated with processmanager yet)
        param:id only find 1 process entry
        param:name match on text in name
        param:nid find logs for specified node
        param:gid find logs for specified grid
        param:aid find logs for specified application type
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes to date specified
        result list(list)
        """
        from_ = self._getEpoch(from_)
        to = self._getEpoch(to)
        params = {'ffrom': {'name': 'epochstart', 'value': from_, 'eq': 'gte'},
                  'to': {'name': 'epochstart', 'value': to, 'eq': 'lte'},
                  'nid': nid,
                  'gid': gid,
                  'id': id,
                  'aid': aid}

        return self.osis_process.simpleSearch(params)

    def getApplications(self, id, type, descr, **kwargs):
        """
        list known application types (applicationtype in osis)
        param:id only find 1 process entry
        param:type
        param:descr match on text in descr
        result list(list)
        """
        params = {'type': type,
                  'id': id,
                  'descr': descr}

        return self.osis_application.simpleSearch(params)

    def getGrids(self, **kwargs):
        """
        list grids
        result list(list)
        """
        return self.osis_grid.simpleSearch({})

    def getJumpscript(self, jsorganization, jsname, **kwargs):
        """
        calls internally the agentcontroller to fetch detail for 1 jumpscript
        param:jsorganization
        param:jsname
        """
        return j.clients.agentcontroller.getJumpscript(jsorganization, jsname)

    def getJumpscripts(self, jsorganization, **kwargs):
        """
        calls internally the agentcontroller
        return: lists the jumpscripts with main fields (organization, name, category, descr)
        param:jsorganization find jumpscripts
        """
        return j.clients.agentcontroller.listJumpScripts(jsorganization)

    def getAgentControllerActiveJobs(self, **kwargs):
        """
        calls internally the agentcontroller
        list jobs now running on agentcontroller
        """
        return j.clients.agentcontroller.getActiveJobs()

    def getAgentControllerSessions(self, roles, nid, active, **kwargs):
        """
        calls internally the agentcontroller
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:nid find for specified node (on which agents are running which have sessions with the agentcontroller)
        param:active is session active or not
        """
        sessions = j.clients.agentcontroller.listSessions()
        def myfilter(session):
            if roles and not set(roles).issubset(set(session['roles'])):
                return False
            if active and not session['activejob']:
                return False
            # TODO nid?
            return True

        return filter(myfilter, sessions)

    def _getEpoch(self, time):
        if not time:
            return time
        if isinstance(time, int):
            return time
        if time.startswith('-'):
            return j.base.time.getEpochAgo(time)
        return j.base.time.getEpochFuture(time)

    def getAlerts(self, id, level, descr, descrpub, nid, gid, category, tags, state, from_inittime, to_inittime, from_lasttime, to_lasttime, from_closetime, to_closetime, nrerrorconditions, errorcondition, **kwargs):
        """
        interface to get alert (is optionally the result of an eco)
        param:id only find 1 alert entry
        param:level level between 1 & 3; all levels underneath are found e.g. level 3 means all levels, 1:critical, 2:warning, 3:info
        param:descr match on text in descr
        param:descrpub match on text in descrpub
        param:nid find alerts for specified node
        param:gid find alerts for specified grid
        param:category match on multiple categories; are comma separated
        param:tags comma separted list of tags/labels
        param:state NEW ALERT CLOSED
        param:from_inittime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts from date specified when they happened first (-4d means 4 days ago)
        param:to_inittime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts to date specified when they happened first
        param:from_lasttime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts from date specified when they happened last  (-4d means 4 days ago)
        param:to_lasttime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts to date specified when they happened last
        param:from_closetime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts from date specified when they were closed  (-4d means 4 days ago)
        param:to_closetime -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find alerts to date specified when they were closed
        param:nrerrorconditions nr of times errorcondition happened
        param:errorcondition errorcondition(s) which caused this alert
        """
        from_inittime = self._getEpoch(from_inittime)
        to_inittime = self._getEpoch(to_inittime)
        from_lasttime = self._getEpoch(from_lasttime)
        to_lasttime = self._getEpoch(to_lasttime)
        from_closetime = self._getEpoch(from_closetime)
        to_closetime = self._getEpoch(to_closetime)
        params = {'id': id,
                  'level': {'name': 'level', 'eq': 'lte', 'value': level},
                  'from_inittime': {'name': 'inittime', 'eq': 'lte', 'value': from_inittime},
                  'to_inittime': {'name': 'inittime', 'eq': 'gte', 'value': to_inittime},
                  'from_lasttime': {'name': 'lasttime', 'eq': 'lte', 'value': from_lasttime},
                  'to_lasttime': {'name': 'lasttime', 'eq': 'gte', 'value': to_lasttime},
                  'from_closetime': {'name': 'closetime', 'eq': 'lte', 'value': from_closetime},
                  'to_closetime': {'name': 'closetime', 'eq': 'gte', 'value': to_closetime},
                  'descrpub': descrpub,
                  'nid': nid,
                  'gid': gid,
                  'category': category,
                  'tags': tags,
                  'state': state,
                  'nrerrorconditions': nrerrorconditions,
                  'errorcondition': errorcondition,
                 }
        return self.osis_alert.simpleSearch(params)

    def getVDisks(self, id, machineid, guid, gid, nid, fs, sizeFrom, sizeTo, freeFrom, freeTo, sizeondiskFrom, sizeondiskTo, mounted, path, description, mountpoint, role, type, order, devicename, backup, backuplocation, backuptime, backupexpiration, active, **kwargs):
        """
        list found vdisks (virtual disks like qcow2 or sections on fs as used by a container or virtual machine) (comes from osis)
        param:id find based on id
        param:machineid to which machine is the vdisk attached
        param:guid find based on guid
        param:gid find vdisks for specified grid
        param:nid find vdisks for specified node
        param:fs ext4;xfs;...
        param:sizeFrom in MB
        param:sizeTo in MB
        param:freeFrom in MB
        param:freeTo in MB
        param:sizeondiskFrom in MB
        param:sizeondiskTo in MB
        param:mounted is disk mounted
        param:path match on part of path e.g. /dev/sda
        param:description match on part of description
        param:mountpoint match on part of mountpoint
        param:role type e.g. BOOT DATA CACHE
        param:type type e.g. QCOW2 FS
        param:order when more vdisks linked to a vmachine order of linkage
        param:devicename if known device name in vmachine
        param:backup is this a backup image
        param:backuplocation where is backup stored (tag based notation)
        param:backuptime epoch when was backup taken
        param:backupexpiration when does backup needs to expire
        param:active True,is the disk still active
        result list(list)
        """
        params = {'id': id,
                  'machineid': machineid,
                  'guid': guid,
                  'gid': gid,
                  'nid': nid,
                  'fs': fs,
                  'sizeFrom': {'name': 'size', 'eq': 'lte', 'value': mbToKB(sizeFrom)},
                  'sizeTo': {'name': 'size', 'eq': 'gte', 'value': mbToKB(sizeTo)},
                  'freeFrom': {'name': 'free', 'eq': 'lte', 'value': mbToKB(freeFrom)},
                  'freeTo': {'name': 'free', 'eq': 'gte', 'value': mbToKB(freeTo)},
                  'sizeondiskFrom': {'name': 'sizeondisk', 'eq': 'lte', 'value': mbToKB(sizeondiskFrom)},
                  'sizeondiskTo': {'name': 'sizeondisk', 'eq': 'gte', 'value': mbToKB(sizeondiskTo)},
                  'mounted': mounted,
                  'path': path,
                  'description': description,
                  'mountpoint': mountpoint,
                  'role': role,
                  'type': type,
                  'order': order,
                  'devicename': devicename,
                  'backup': backup,
                  'backuplocation': backuplocation,
                  'backupexpiration': backupexpiration,
                  'backuptime': backuptime,
                  'active': active,
                 }
        return self.osis_vdisk.simpleSearch(params)

    def getMachines(self, id, guid, otherid, gid, nid, name, description, state, roles, ipaddr, macaddr, active, cpucore, mem, type, **kwargs):
        """
        list found machines (comes from osis)
        param:id find based on id
        param:guid find based on guid
        param:otherid find based on 2nd id
        param:gid find nodes for specified grid
        param:nid find nodes for specified node
        param:name match on text in name
        param:description match on text in name
        param:state STARTED,STOPPED,RUNNING,FROZEN,CONFIGURED,DELETED
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:ipaddr comma separated list of ip addr to match against
        param:macaddr comma separated list of mac addr to match against
        param:active True,is the machine still active
        param:cpucore find based on nr cpucore
        param:mem find based on mem in MB
        param:type KVM or LXC
        result list(list)
        """
        params = {'id': id,
                  'guid': guid,
                  'otherid': otherid,
                  'gid': gid,
                  'nid': nid,
                  'name': name,
                  'description': description,
                  'state': state,
                  'active': active,
                  'cpucore': cpucore,
                  'mem': mem,
                  'type': type,}

        def myfilter(machine):
            if roles and not set(roles).issubset(set(machine['roles'])):
                return False
            if ipaddr and ipaddr not in machine['ipaddr']:
                return False
            if macaddr and macaddr not in machine['netaddr']:
                return False
            return True

        results = self.osis_machine.simpleSearch(params)
        return filter(myfilter, results)

    def getDisks(self, id, guid, gid, nid, fs, sizeFrom, sizeTo, freeFrom, freeTo, mounted, ssd, path, model, description, mountpoint, type, active, **kwargs):
        """
        list found disks (are really partitions) (comes from osis)
        param:id find based on id
        param:guid find based on guid
        param:gid find disks for specified grid
        param:nid find disks for specified node
        param:fs ext4;xfs;...
        param:sizeFrom in MB
        param:sizeTo in MB
        param:freeFrom in MB
        param:freeTo in MB
        param:mounted is disk mounted
        param:ssd is disk an ssd
        param:path match on part of path e.g. /dev/sda
        param:model match on part of model
        param:description match on part of description
        param:mountpoint match on part of mountpoint
        param:type type e.g. BOOT DATA CACHE
        param:active True,is the disk still active
        result list(list)
        """
        params = {'id': id,
                  'guid': guid,
                  'gid': gid,
                  'nid': nid,
                  'fs': fs,
                  'sizeFrom': {'name': 'size', 'eq': 'lte', 'value': mbToKB(sizeFrom)},
                  'sizeTo': {'name': 'size', 'eq': 'gte', 'value': mbToKB(sizeTo)},
                  'freeFrom': {'name': 'free', 'eq': 'lte', 'value': mbToKB(freeFrom)},
                  'freeTo': {'name': 'free', 'eq': 'gte', 'value': mbToKB(freeTo)},
                  'mounted': mounted,
                  'ssd': ssd,
                  'path': path,
                  'model': model,
                  'description': description,
                  'mountpoint': mountpoint,
                  'type': type,
                  'active': active,
                 }
        return self.osis_disk.simpleSearch(params)


