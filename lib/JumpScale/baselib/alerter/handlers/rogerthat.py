from JumpScale import j
from JumpScale.lib.rogerthat.rogerthatservice import GeventWSServer
from JumpScale.baselib.alerter.alerts_service import Handler
import json
import gevent

class RogerThatAlerter(Handler):
    ORDER = 10
    ANSWERS = [{'id': 'accept', 'caption': 'Accept', 'action': '', 'type': 'button'},{'id': 'escalate', 'caption': 'Escalate', 'action': '', 'type': 'button'}]

    def __init__(self, service):
        self.service = service
        self.rogerthathandler = RogerThatHandler(self)
        self.rogerthatserver = GeventWSServer('0.0.0.0', 5005, self.rogerthathandler)
        self.registeredusers = set()
        self.loadFriends()

    def loadFriends(self):
        for friend in self.rogerthathandler.client.retreive_users():
            self.registeredusers.add(friend['email'])

    def escalate(self, alert, users):
        emails = list()
        users = users[:]
        for user in users[:]:
            useremails = self.service.getUserEmails(user)
            if self.registeredusers.intersection(useremails):
                emails.append(user['emails'])
                users.remove(user)

        message = self.makeMessage(alert)
        answers = self.ANSWERS[:]
        url = self.service.getUrl(alert)
        answers.append({'id': 'details', 'caption': 'Details', 'action': url, 'type':'button'})
        message_id = self.rogerthathandler.send_message(message=message, members=emails, answers=answers, tag=alert['guid'])
        alert['message_id'] = message_id
        self.service.rediscl.hset('alerts', alert['guid'], json.dumps(alert))
        return users

    def updateState(self, alert):
        self.rogerthathandler.send_message(message="User %(assigned_user)s has accepted " % alert, flags=17, parent_message_key=alert['message_id'], alert_flags=0)

    def start(self):
        return gevent.spawn(self.rogerthatserver.start)

    def makeMessage(self, alert):
        message = """An event has happend on the Mothership1 cloud please investigate.
Level: %(level)s
Message: %(errormessage)s
"""  % alert
        return message

class RogerThatHandler(object):
    API_KEY = j.application.config.get('rogerthat.apikey')

    def __init__(self, service):
        self.service = service
        self.alerter = service.service
        self.alerts_client = self.alerter.pcl.actors.system.alerts
        self.client = j.clients.rogerthat.get(self.API_KEY)

    def send_message(self, **kwargs):
        result = self.client.send_message(**kwargs)
        if result:
            if result['error']:
                print('Could not send rogerthat message. Message: %(message)s' % result['error'])
                return
            else:
                message_id = result['result']
                return message_id

    def messaging_update(self, params):
        if params['status'] == 1: # user received messageS
            return
        elif params['status'] & 2 == 2:
            user = params['user_details'][0]
            useremail = user['email']
            user = self.getUserByEmail(useremail)
            if params['answer_id'] == 'accept':
                self.alerts_client.update(state='ACCEPTED', alert=params['tag'], comment='Via Rogerthat', username=user['id'])
            elif params['answer_id'] == 'escalate':
                self.alerts_client.escalate(alert=params['tag'], comment='Via Rogerthat', username=user['id'])

    def getUserByEmail(self, email):
        users = self.alerter.scl.user.search({'emails': email})[1:]
        if users:
            return users[0]
        return None

    def friend_invited(self, params):
        email = params['user_details'][0]['email']
        user = self.getUserByEmail(email)
        if user:
            for group in user['groups']:
                if group.startswith('level'):
                    self.service.registeredusers.add(email)
                    return 'accepted'
        return 'declined'

    def __getattr__(self, key):
        def wrapper(params):
            print "Method %s not implemented" % key
            return
        return wrapper
