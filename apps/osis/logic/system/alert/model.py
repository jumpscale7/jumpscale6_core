from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Alert(OsisBaseObject):

    """
    alert object
    """

    def __init__(self, ddict={},id=0,guid="",description="",descriptionpub="",level=1,category="",tags="",transactionsinfo=""   ):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.init("eco","1.0")
            self.id=id  #is unique where alert has been created
            if guid=="":
                self.guid=j.base.idgenerator.generateGUID() #can be used for authentication purposes
            else:
                self.guid=guid
            self.description=description
            self.descriptionpub=descriptionpub
            self.level=level #1:critical, 2:warning, 3:info
            self.category=category #dot notation e.g. machine.start.failed
            self.tags=tags #e.g. machine:2323
            self.state="NEW" #["NEW","ALERT","CLOSED"]
            self.inittime=0 #first time there was an error condition linked to this alert
            self.lasttime=0 #last time there was an error condition linked to this alert
            self.closetime=0  #alert is closed, no longer active
            self.nrerrorconditions=1 #nr of times this error condition happened
            self.errorconditions=[]  #ids of errorconditions     
