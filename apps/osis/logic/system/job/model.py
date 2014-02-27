from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Job(OsisBaseObject):

    """
    identifies a job in the grid
    """

    def __init__(self, ddict={}, gid="", roles=None, args=None, timeout=60, sessionid=None, jscriptid=None,\
            nid=0,cmd="",category="",log=True, queue=None):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id=0
            self.sessionid = sessionid
            self.gid =gid
            self.nid =nid
            self.cmd = cmd
            self.category = category
            if not roles:
                roles = list()
            if not args:
                args = dict()
            self.roles=roles
            self.args=args
            self.queue=queue
            self.timeout=timeout
            self.result=None
            self.parent=None
            self.resultcode=None
            self.state="SCHEDULED" #SCHEDULED,STARTED,ERROR,OK,NOWORK
            self.timeStart=j.base.time.getTimeEpoch()
            self.timeStop=0
            self.log=log

    def getUniqueKey(self):
        return j.base.idgenerator.generateGUID()

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.nid = int(self.nid)
        self.id = int(self.id)
        self.guid = "%s_%s_%s" % (self.gid, self.nid,self.id)
        return self.guid
