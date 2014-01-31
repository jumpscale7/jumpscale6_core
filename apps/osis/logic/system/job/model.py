from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Job(OsisBaseObject):

    """
    identifies a job in the grid
    """

    def __init__(self, ddict={}, gid="",jsname='', jsorganization='', role="", args=[], timeout=60, sessionid=None, jscriptid=None,\
            nid=0,cmd="",category="",log=True):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id=0
            self.sessionid=sessionid
            self.gid =gid
            self.nid =nid
            self.jsname = jsname
            self.jsorganization=jsorganization
            self.cmd=""
            self.category=""
            self.role=role
            self.args=args
            self.timeout=timeout
            self.result=None
            self.parent=None
            self.resultcode=None
            self.state="SCHEDULED" #SCHEDULED,STARTED,ERROR,OK,NOWORK
            self.timeStart=j.base.time.getTimeEpoch()
            self.timeStop=0
            self.log=log

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.id = int(self.id)
        self.guid = "%s_%s" % (self.gid, self.id)
        return self.guid

            

       
