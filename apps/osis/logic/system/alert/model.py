from JumpScale import j

OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

class Alert(OsisBaseObject):

    """
    alert object
    history = [{'user':'hamdy', 'state':'ACCEPTED', 'epoch':123, 'comment':''}, {'user':'hamdy', 'state':'RESOLVED', 'epoch':123, 'comment':''}]

    """
    ALLOWED_STATES = ["NEW","ALERT", 'ACCEPTED',  'RESOLVED',  'UNRESOLVED', 'CLOSED']

    def __init__(self,
                ddict={},
                id=0,
                gid=0,
                nid=0,
                guid="",
                aid=0,
                jid=0,
                masterjid=0,
                epoch=0,
                errormessage="",
                errormessagePub="",
                description="",
                descriptionpub="",
                level=1,
                category="",
                tags="",
                inittime=0,#first time there was an error condition linked to this alert
                lasttime=0,#last time there was an error condition linked to this alert
                closetime=-1,#alert is closed, no longer active
                transactionsinfo="",
                slabreach=0,
                history=[],
                state='NEW',
                assigned_user=None,
                eco=None):

        if ddict <> {}:
            self.load(ddict)
        else:
            self.id=id  #is unique where alert has been created
            if guid=="":
                self.guid=j.base.idgenerator.generateGUID() #can be used for authentication purposes
            else:
                self.guid=guid
            self.gid = gid
            self.nid = nid
            self.description=description
            self.descriptionpub=descriptionpub
            self.level=level #1:critical, 2:warning, 3:info
            self.category=category #dot notation e.g. machine.start.failed
            self.tags=tags #e.g. machine:2323
            self.inittime = inittime #first time there was an error condition linked to this alert
            self.lasttime = lasttime #last time there was an error condition linked to this alert
            self.closetime= closetime  #alert is closed, no longer active
            self.nrerrorconditions=1 #nr of times this error condition happened
            self.errorconditions=[]  #ids of errorconditions
            
            self.assigned_user = assigned_user
            
            self.update_state(state) #["NEW","ALERT", 'ACCEPTED',  'RESOLVED',  'UNRESOLVED', 'CLOSED']

            self.lasttime=0 #last time there was an error condition linked to this alert
            self.closetime=0  #alert is closed, no longer active

            self.occurrences=1 #nr of times this error condition happened
            self.slabrach = slabreach
            self.history = history
            self.eco = eco
            
            self.aid = aid
            self.jid = jid
            self.masterjid = masterjid
            self.epoch = epoch
            self.errormessage = errormessage
            self.errormessagePub = errormessagePub

    def _check_state(self, state):
        if not state in self.ALLOWED_STATES:
            raise RuntimeError('Invalid state -- allowed states are %s' % self.ALLOWED_STATES)

    def _check_history_item(self, history_item):
        for item in ['user', 'state', 'epoch', 'comment']:
            if not item in history_item:
                raise RuntimeError('Invalid history item -- missing %s' % item)

    def update_state(self, state):
        self._check_state(state)
        self.state = state

    def update_history(self, history_item):
        self._check_history_item(history_item)
        self.history.insert(0, history_item)
        self.assigned_user = history_item['user']

    def pprint_history(self):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.history)

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.id = int(self.id)
        self.guid = "%s_%s" % (self.gid, self.id)
        return self.guid

    