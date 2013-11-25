from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Job(OsisBaseObject):

    """
    identifies a job in the grid
    """

    def __init__(self, ddict={}):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id= j.base.idgenerator.generateGUID()
            self.jsname = jsname
            self.jsorganization=jsorganization
            self.roles=roles
            self.args=args
            self.timeout=timeout
            self.result=None
            self.sessionid=sessionid
            self.jscriptid=jscriptid
            self.event=None
            self.children=[]
            self.childrenActive={}
            self.parent=None
            self.resultcode=None

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.id

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.guid = self.id
        return self.id
