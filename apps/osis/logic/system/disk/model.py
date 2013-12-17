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


    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.guid

