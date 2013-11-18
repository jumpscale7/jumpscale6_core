from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Node(OsisBaseObject):

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

