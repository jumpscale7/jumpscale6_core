from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Node(OsisBaseObject):

    """
    identifies a node in the grid
    @param netaddr = {mac:[ip1,ip2]}
    """

    def __init__(self, ddict={}, roles=[], name="", netaddr={}, machineguid="", id=0):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.init("node","1.0")
            self.id = id
            self.gid = 0
            self.name = name
            self.roles = roles
            self.netaddr = netaddr
            self.guid = None
            self.machineguid = machineguid

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

        if self.gid == None:
            self.gid = q.grid.id
        # self.sguid=struct.pack("<HH",self.gid,self.id)
        self.guid = "%s_%s" % (self.gid, self.id)
        return self.guid

