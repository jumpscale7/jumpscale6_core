from JumpScale import j

class system_alerts(j.code.classGetBase()):

    """
    Alerts handler
    
    """

    def __init__(self):

        self._te = {}
        self.actorname = "alertshandler"
        self.appname = "system"
        self.scl = j.core.osis.getClientForNamespace('system', j.core.portal.active.osis)


    def update(self, state, alert, comment=None, username=None, **kwargs):
        """
        process eco 
        first find duplicates for eco (errorcondition obj of style as used in this actor)
        the store in db
        """
        if not self.scl.alert.exists(alert):
            raise RuntimeError('Invalid Alert')

        alert_obj =  self.scl.alert.get(alert)
        
        if username and not self.scl.user.search({'id':username})[0]:
            raise RuntimeError('User %s does not exist' % username)

        # only state ACCEPT can have username passed
        if username and state != 'ACCEPTED':
            raise RuntimeError('Invalid operation')

        username = username or kwargs['ctx'].env['beaker.session']['user']
        comment = comment or ''
        epoch = j.base.time.getTimeEpoch()
        
        history = {'user':username,
                   'state':state,
                   'comment':comment,
                   'epoch':epoch}
        
        alert_obj.update_state(state)
        
        if not hasattr(alert_obj, 'history'):
            alert_obj.history = []
        
        alert_obj.update_history(history)
        
        self.scl.alert.set(alert_obj)

        return True