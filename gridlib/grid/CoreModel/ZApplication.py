from OpenWizzy import o
import struct

from ZBase import ZBase

class ZApplication(ZBase):
    """
    identifies a type of application in the cloud
    """
    def __init__(self, ddict={},name="",description=""):
        if ddict<>{}:
            self.__dict__=ddict
        else:     
            self.id=0
            self.bid=o.core.grid.bid
            self.gid=o.core.grid.id
            self.name=name
            self.description=description
            self.guid=None
            self.sguid=None   
        print self.bid       

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
        self.gid=int(self.gid)
        self.id=int(self.id)
        self.bid=int(self.bid)
        self.sguid=struct.pack("<HHH",self.gid,self.bid,self.id)
        self.guid="%s_%s_%s"%(self.gid,self.bid,self.id)
        return self.guid

    def getIDs(self):
        """
        return (gid,id)
        gid=grid id
        bid=broker id
        id=unique int id for obj in grid_broker
        """
        return struct.unpack("<HHH",self.sguid)

    def getGuidParts(self):
        return ["gid","bid","id"]

    def getObjectType(self):
        return 11

    def getVersion(self):
        return 1

    def getMessage(self):
        #[$objecttype,$objectversion,guid,$object=data]
        return [11,1,self.sguid,self.__dict__]
