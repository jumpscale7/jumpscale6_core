from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class ECO(OsisBaseObject):

    """
    error condition object
    """

    def __init__(self, ddict={},id=0,guid="",errormessage="",errormessagePub="",level=1,category="",tags="",transactionsinfo="",\
                    gid=0,nid=0,pid=0,aid=0,jid=0,masterjid=0,epoch=0,type=0):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.errormessage=errormessage
            self.errormessagePub=errormessagePub
            self.level=int(level) #1:critical, 2:warning, 3:info
            self.category=category #dot notation e.g. machine.start.failed
            self.tags=tags #e.g. machine:2323

            self.errormessage=errormessage
            self.errormessagePub=errormessagePub

            self.code=""
            self.funcname=""
            self.funcfilename=""
            self.funclinenr=0
            self.backtrace=""

            self.appname=j.application.appname #name as used by application

            self.id=0

            self.gid = gid
            self.nid = nid

            self.aid = aid
            self.pid = pid
            self.jid = jid
            self.masterjid = masterjid

            if epoch==0:
                self.epoch= j.base.time.getTimeEpoch()
            else:
                self.epoch=epoch

            self.type=int(type) #j.enumerators.ErrorConditionType                       

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.getSetGuid()

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        if not self.guid:
            self.gid = int(self.gid)
            self.id = int(self.id)
            self.guid = "%s_%s" % (self.gid, self.id)
        return self.guid

