from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Fake4Test(OsisBaseObject):

    """
    identifies a node in the grid
    @param netaddr = {mac:[ip1,ip2]}
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.init("node","1.0")
            self.id = 0
            self.gid = 0
            self.name = ""
            self.roles = []
            self.netaddr = None
            self.guid = None
            self.machineguid = ""
            self.ipaddr=[]
            self.active = True
            self.peer_stats=0 #node which has stats for this node
            self.peer_log=0 #node which has transactionlog or other logs for this node
            self.peer_backup=0 #node which has backups for this node
            self.description=""
            self.lastcheck=0 #epoch of last time the info was checked from reality


    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.machineguid

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.id = int(self.id)

        # self.sguid=struct.pack("<HH",self.gid,self.id)
        self.guid = "%s_%s" % (self.gid, self.id)
        self.lastcheck=j.base.time.getTimeEpoch() 

        return self.guid

    def initFromLocalNodeInfo(self):
        """
        get ipaddr info & gid & nid from local config
        """

        self.machineguid = j.application.getUniqueMachineId().replace(":", "")
        self.roles= j.application.config.get("grid.node.roles").split(",")

        self.ipaddr=[item for item in j.system.net.getIpAddresses() if item <>"127.0.0.1"]        
        
        self.netaddr=j.system.net.getNetworkInfo()

        self.gid=j.application.config.getInt("grid.id")
        if self.gid==0:
            raise RuntimeError("grid id cannot be 0")

