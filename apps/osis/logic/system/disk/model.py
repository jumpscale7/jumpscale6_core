from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Disk(OsisBaseObject):

    """
    identifies a disk in the grid
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.init("disk","1.0")
            self.id = 0
            self.gid = 0
            self.nid = 0
            self.path = ""
            self.size = 0 #KB
            self.free = 0 #KB
            self.ssd=False
            self.fs=""
            self.mounted=False
            self.mountpoint=""
            self.guid = None
            self.active = True
            self.model=""
            self.description=""
            self.type=""  #BOOT,DATA,...
            self.lastcheck=0 #epoch of last time the info was checked from reality


    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        C="%s_%s_%s_%s_%s"%(self.gid,self.nid,self.path,self.ssd,self.type)
        return j.tools.hash.md5_string(C)

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.id = int(self.id)
        self.guid = "%s_%s" % (self.gid, self.id)
        self.lastcheck=j.base.time.getTimeEpoch() 
        return self.guid

