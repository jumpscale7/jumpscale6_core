from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Group(OsisBaseObject):

    """
    identifies a node in the grid
    @param netaddr = {mac:[ip1,ip2]}
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id = ""
            self.domain=""
            self.gid = j.application.whoAmI.gid
            self.roles = []
            self.active = True
            self.description=""
            self.lastcheck=0 #epoch of last time the info updated
            self.guid=""
            self.users=[]

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.id = self.id

        # self.sguid=struct.pack("<HH",self.gid,self.id)
        self.guid = "%s_%s"%(self.gid,self.id)
        self.lastcheck=j.base.time.getTimeEpoch() 

        return self.guid

