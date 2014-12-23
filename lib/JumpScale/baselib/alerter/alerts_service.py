from JumpScale import j
import JumpScale.grid.osis
import JumpScale.baselib.redis
import JumpScale.lib.rogerthat
import JumpScale.portal

try:
    import ujson as json
except ImportError:
    import json
import time
import sys
import os
import inspect
import gevent

class Handler(object):
    ORDER = 50

    def __init__(self, service):
        self.service = service

    def start(self):
        pass

    def updateState(self, alert):
        pass

    def escalate(self, alert, users):
        pass

class AlertService(object):

    def __init__(self):
        self.rediscl = j.clients.redis.getByInstanceName('system')
        self.alertqueue = self.rediscl.getQueue('alerts')
        self.pcl = j.core.portal.getClientByInstance('main')
        self.scl = j.core.osis.getClientForNamespace('system')
        self.handlers = list()
        self.loadHandlers()

    def log(self, message, level=1):
        j.logger.log(message, level, 'alerter')

    def getUsersForLevel(self, level):
        groupname = "level%s" % level
        users = self.scl.user.search({'groups': groupname, 'active': True})[1:]
        return users

    def getUserEmails(self, user):
        useremails = user['emails']
        if not isinstance(useremails, list):
            useremails = [useremails]
        return useremails

    def loadHandlers(self):
        from JumpScale.baselib.alerter import handlers
        for name, module in inspect.getmembers(handlers, inspect.ismodule):
            for name, klass in inspect.getmembers(module, inspect.isclass):
                if issubclass(klass, Handler) and klass is not Handler:
                    self.handlers.append(klass(self))
        self.handlers.sort(key=lambda s: s.ORDER)

    def getUrl(self, alert):
        return "http://cpu01.bracknell1.vscalers.com:8282/grid/alert?id=%(guid)s" % alert

    def escalate(self, alert):
        level = alert['level']
        users = self.getUsersForLevel(level)
        for handler in self.handlers:
            result = handler.escalate(alert, users)
            if result is not None:
                users = result

    def updateState(self, alert):
        for handler in self.handlers:
            handler.updateState(alert)

    def getAlert(self, id):
        return self.scl.alert.get(id).dump()

    #def escalate_L2(message, message_id):
    #    message_data = json.loads(redis_client.hget('messages', message_id))
    #    if message_data['state'] == 'L1':
    #        # hash 'contacts' contains keys 1, 2, 3 and all with rogerthat ids
    #        contact2 = redis_client.hget('contacts', '2')
    #        contact3 = redis_client.hget('contacts', '3')
    #        contacts = [contact2, contact3]
    #        send_message(message, contacts)
    #        epoch = time.time()
    #        message_data = {'epoch': epoch, 'state': 'L2', 'log': '%s: %s %s' % (epoch, ', '.join(contacts), 'L2'), 'message': message}
    #        redis_client.hset('messages', message_id, json.dumps(message_data))

    #def escalate_L3(message, message_id):
    #    message_data = json.loads(redis_client.hget('messages', message_id))
    #    if message_data['state'] == 'L2':
    #        # hash 'contacts' contains keys 1, 2, 3 and all with rogerthat ids
    #        contacts = json.loads(redis_client.hget('contacts', 'all'))
    #        send_message(message, contacts)
    #        epoch = time.time()
    #        message_data = {'epoch': epoch, 'state': 'L3', 'log': '%s: %s %s' % (epoch, ', '.join(contacts), 'L3'), 'message': message}
    #        redis_client.hset('messages', message_id, json.dumps(message_data))

    def start(self):
        for handler in self.handlers:
            handler.start()
        greenlet = gevent.spawn(self.receiveAlerts)
        gevent.joinall([greenlet])


    def receiveAlerts(self):
        while True:
            alertid = self.alertqueue.get()
            alert = self.getAlert(alertid) 
            oldalert = self.rediscl.hget('alerts', alertid)
            self.rediscl.hset('alerts', alert['guid'], json.dumps(alert))
            self.log('Got alertid %s' % alertid)
            if alert['state'] == 'ALERT':
                self.escalate(alert=alert)
            elif oldalert:
                oldalert = json.loads(oldalert)
                if oldalert['state'] == 'ALERT' and alert['state'] == 'ACCEPTED':
                    self.rediscl.hdel('alerts', alert['guid'])
                    alert['message_id'] = oldalert['message_id']
                    self.updateState(alert)
            #alert = json.loads(alert_json)
            #if alert['state'] == 'CRITICAL':
            #    # escalate L1

            # escalate L2 after 5 mins
            #gevent.spawn_later(escalate_L2, 300.0, message=message, message_id=message_id)

            # escalate L3 after 15 mins
            #gevent.spawn_later(escalate_L3, 1200.0, message=message, message_id=message_id)

