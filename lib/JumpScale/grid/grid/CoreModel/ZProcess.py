from JumpScale import j
import struct

from ZBase import ZBase


class ZProcess(ZBase):

    """
    identifies a type of application in the cloud
    """

    def __init__(self, ddict={}, name="", description="", type="", instance=0, systempid=0):
        if ddict <> {}:
            self.__dict__ = ddict
        else:
            self.id = 0
            self.bid = j.core.grid.bid
            self.gid = j.core.grid.id
            self.aid = j.core.grid.aid  # application id which is unique per broker, application type which asked for this job (is a type not a specific instance of an app)
            self.nid = j.core.grid.nid
            self.name = name
            self.type = type
            self.description = description
            self.instance = instance
            self.systempid = systempid  # system process id (PID) at this point
            self.guid = None
            self.sguid = None
            self.epochstart = j.base.time.getTimeEpoch()
            self.epochstop = 0

    def getCategory(self):
        return "zapplication"

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.getContentKey()

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.bid = int(self.bid)
        self.id = int(self.id)
        # self.sguid=struct.pack("<HHL",self.gid,self.bid,self.id)
        self.guid = "%s_%s_%s" % (self.gid, self.bid, self.id)
        return self.guid

    def getIDs(self):
        """
        return (gid,id)
        gid=grid id
        bid=broker id
        id=unique int id for obj in grid_broker
        """
        return struct.unpack("<HHH", self.sguid)

    def getGuidParts(self):
        return ["gid", "bid", "id"]

    def getObjectType(self):
        return 12

    def getVersion(self):
        return 1

    def getMessage(self):
        #[$objecttype,$objectversion,guid,$object=data]
        return [12, 1, self.sguid, self.__dict__]
