from JumpScale import j
import struct

from ZBase import ZBase


class ZNode(ZBase):

    """
    identifies a node in the grid
    @param netaddr = {mac:[ip1,ip2]}
    """

    def __init__(self, ddict={}, roles=[], name="", netaddr={}, machineguid="", id=0):
        if ddict <> {}:
            self.__dict__ = ddict
        else:
            self.id = id
            self.gid = 0
            self.name = name
            self.roles = roles
            self.netaddr = netaddr
            self.guid = None
            self.sguid = None
            self.machineguid = machineguid

    def getCategory(self):
        return "znode"

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

    def getIDs(self):
        """
        return (gid,id)
        gid=grid id
        id=unique int id for obj
        """
        return struct.unpack("<HH", self.sguid)

    def getGuidParts(self):
        return ["gid", "id"]

    def getObjectType(self):
        return 10

    def getVersion(self):
        return 1

    def getMessage(self):
        #[$objecttype,$objectversion,guid,$object=data]
        return [10, 1, self.sguid, self.__dict__]
