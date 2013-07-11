from OpenWizzy import o
import struct

from ZBase import ZBase

class ZAction(ZBase):
    def __init__(self, ddict={},name="",code="",md5="",path="",category="", errordescr="",recoverydescr="", maxtime=0):
        if ddict<>{}:
            self.__dict__=ddict
        else:     
            self.id=0
            self.gid=o.core.grid.id
            self.bid=o.core.grid.bid #broker id
            self.name=name
            self.code=code
            if md5=="":
                self.codemd5=o.tools.hash.md5_string(self.code)
            else:
                self.codemd5=md5
            self.path=path
            self.category=category #e.g. actor.system.createowpackage  or mytest.something  (is free but can point to an actormethod)
            self.errordescr=errordescr
            self.recoverydescr=recoverydescr
            self.maxtime=maxtime
            self.guid=None
            self.moddate=o.base.time.getTimeEpoch()
            self.sguid=None       


    def getCategory(self):
        return "zaction"

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return o.tools.hash.md5_string(str(self.gid)+str(self.bid)+str(self.name)+self.codemd5+self.path+self.category+self.errordescr+self.recoverydescr+str(self.maxtime))

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid=int(self.gid)
        self.bid=int(self.bid)
        self.id=int(self.id)
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
        return 13

    def getVersion(self):
        return 1

    def getMessage(self):
        #[$objecttype,$objectversion,guid,$object=data]
        return [13,1,self.sguid,self.__dict__]
