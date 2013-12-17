from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class ApplicationType(OsisBaseObject):

    """
    identifies type of application
    """

    def __init__(self, ddict={}, name="",description="",type="",gid=0):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.init("applicationtype","1.0")
            self.id = 0
            self.gid = gid
            self.name = name
            self.description = description
            self.type = type
            self.active = True

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
        self.id = int(self.id)
        self.guid = "%s_%s" % (self.gid, self.id)
        return self.guid
