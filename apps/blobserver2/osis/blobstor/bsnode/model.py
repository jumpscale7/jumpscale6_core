from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class BlobStorNode(OsisBaseObject):

    """
    identifies a node which represents a blobstor
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id=0
            self.nid = 0
            self.gid = 0
            self.size = 0 #GB
            self.free = 0 #GB
            self.guid = None
            self.active = True
            self.lastupdate=0 #epoch of last time the info was updated from reality
        self.getSetGuid()

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        C="%s_%s"%(self.gid,self.nid)
        return j.tools.hash.md5_string(C)

    def getContentKey(self):
        C="%s_%s_%s_%s_%s"%(self.gid,self.nid,self.size,self.free,self.active)
        return j.tools.hash.md5_string(C)

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.guid = "%s_%s" % (self.gid, self.id)
        self.lastupdate=j.base.time.getTimeEpoch()
        return self.guid

