from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class VDisk(OsisBaseObject):

    """
    identifies a disk in the grid
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.init("vdisk","1.0")
            self.id = 0
            self.guid = None
            self.gid = 0
            self.nid = 0
            self.path = ""
            self.size = 0 #KB
            self.free = 0 #KB
            self.sizeondisk = 0 #size on physical disk after e.g. compression ... KB
            self.fs=""
            self.active = True
            self.description=""
            self.role=""  #BOOT,DATA,...
            self.machineid=""  #who is using it
            self.order=0
            self.type="" #QCOW2,FS
            self.backup=False
            self.backuptime=0
            self.expiration=0
            self.backuplocation="" #where is backup stored (tag based notation)
            self.devicename=""

        

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.guid

