from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Job(OsisBaseObject):

    """
    identifies a job in the grid
    """

    def __init__(self, ddict={}, jsname='', jsorganization='', roles=[], args=[], timeout=60, sessionid=None, jscriptid=None,lock="",lockduration=3600):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id= j.base.idgenerator.generateGUID().replace('-', '')
            self.jsname = jsname
            self.jsorganization=jsorganization
            self.roles=roles
            self.args=args
            self.timeout=timeout
            self.result=None
            self.sessionid=sessionid
            self.jscriptid=jscriptid
            self.children=[]
            self.childrenActive={}
            self.parent=None
            self.resultcode=None
            self.lock=lock
            self.state="SCHEDULED" #SCHEDULED,STARTED,ERROR,OK,NOWORK
            self.timeStart=j.base.time.getTimeEpoch()
            self.timeStop=0
            self.lock=lock
            self.lockduration=lockduration
            self.description=""
            self.source=""
            self.category=""

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

    def getDict(self):
        """
        Returns a proper serializable dict from the object
        """
        basicdict = self.__dict__.copy()
        basicdict['children'] = []
        for child in self.children:
            childdict = child.__dict__
            basicdict['children'].append(childdict)
        return basicdict
            

       
