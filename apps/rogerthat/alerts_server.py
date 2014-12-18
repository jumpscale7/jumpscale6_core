#! /usr/bin/python
from gevent import monkey
#monkey.patch_all()
monkey.patch_socket()
monkey.patch_ssl()
monkey.patch_thread()
monkey.patch_time()

from JumpScale import j
import JumpScale.grid.osis
import JumpScale.baselib.redis
import JumpScale.lib.rogerthat
import rogerthat_callback_server
import JumpScale.portal

try:
    import ujson as json
except ImportError:
    import json
import time
import gevent

class RogerThatHandler(object):
    API_KEY = j.application.config.get('rogerthat.apikey')
    ANSWERS = [{'id': 'accept', 'caption': 'Accept', 'action': '', 'type': 'button'},]

    def __init__(self, service):
        self.service = service
        self.client = j.clients.rogerthat.get(self.API_KEY)

    def send_message(self, **kwargs):
        result = self.client.send_message(**kwargs)
        if result:
            if result['error']:
                j.logger.log('Could not send rogerthat message')
                return
            else:
                message_id = result['result']
                return message_id

    def messaging_update(self, params):
        if params['status'] == 1: # user received messageS
            return
        elif params['status'] & 2 == 2 and params['answer_id'] == 'accept':
            user = params['user_details'][0]
            # TODO call portal to update alert assignee
            self.send_message(message="User %(name)s has accepted " % user, answers=[], flags=17, parent_message_key=params['parent_message_key'])

    def friend_invited(self, params):
        # TODO validate email is in users and has group level*
        return 'accepted'

    def __getattr__(self, key):
        def wrapper(params):
            print "Method %s not implemented" % key
            return
        return wrapper

class AlertService(object):

    def __init__(self):
        self.rediscl = j.clients.redis.getByInstanceName('system')
        self.alertqueue = self.rediscl.getQueue('alerts')
        self.pcl = j.core.portal.getClientByInstance('main')
        self.rogerthathandler = RogerThatHandler(self)
        self.rogerthatserver = rogerthat_callback_server.GeventWSServer('0.0.0.0', 5005, self.rogerthathandler)
        self.scl = j.core.osis.getClientForNamespace('system')
        

    def makeMessage(self, alert):
        message = """An event has happend on the Mothership1 cloud please investiage:
Message: %(errormessage)s
Level: %(level)s

See http://cpu01.bracknell1.vscalers.com:8282/grid/alert?id=%(guid)s for more details
"""  % alert
        return message


    def getEmailsForLevel(self, level):
        groupname = "level%s" % level
        users = self.scl.user.search({'groups': groupname, 'active': True})[1:]
        return [ u['emails'] for u in users ]


    def escalate(self, level, alert):
        emails = self.getEmailsForLevel(level)
        message = self.makeMessage(alert)
        answers = self.rogerthathandler.ANSWERS[:]
        url = "http://cpu01.bracknell1.vscalers.com:8282/grid/alert?id=%(guid)s" % alert
        answers.append({'id': 'details', 'caption': 'Details', 'action': url, 'type':'button'})
        message_id = self.rogerthathandler.send_message(message=message, members=emails, answers=answers, tag=alert['guid'])
        self.rediscl.hset('alerts', alert['guid'], json.dumps(alert))
        return message_id

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
        greenlets = list()
        greenlets.append(gevent.spawn(self.receiveAlerts))
        self.rogerthatserver.start()
        gevent.joinall(greenlets)


    def receiveAlerts(self):
        while True:
            alertid = self.alertqueue.get()
            alert = self.getAlert(alertid) 
            print 'Got alertid', alertid
            self.escalate(level=1, alert=alert)
            #alert = json.loads(alert_json)
            #if alert['state'] == 'CRITICAL':
            #    # escalate L1

            # escalate L2 after 5 mins
            #gevent.spawn_later(escalate_L2, 300.0, message=message, message_id=message_id)

            # escalate L3 after 15 mins
            #gevent.spawn_later(escalate_L3, 1200.0, message=message, message_id=message_id)


if __name__ == '__main__':
    j.application.start("alerts_server")
    AlertService().start()
    j.application.stop()
