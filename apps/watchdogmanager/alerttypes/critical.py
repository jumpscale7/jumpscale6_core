
from JumpScale import j
import JumpScale.baselib.watchdog.manager
import JumpScale.baselib.redis
import JumpScale.lib.rogerthat

descr = """
critical alert
"""

organization = "jumpscale"
enable = True

REDIS_PORT = 9999
# API_KEY = j.application.config.get('rogerthat.apikey')

redis_client = j.clients.credis.getRedisClient('127.0.0.1', REDIS_PORT)
# rogerthat_client = j.clients.rogerthat.get(API_KEY)

# ANSWERS = [{'id': 'yes', 'caption': 'Take', 'action': '', 'type': 'button'},]

# def _send_message(message, contacts, answers=ANSWERS, alert_flags=6):
#     result = rogerthat_client.send_message(message, contacts, answers=answers, alert_flags=alert_flags)
#     if result:
#         if result['error']:
#             j.logger.log('Could not send rogerthat message')
#             return
#         else:
#             message_id = result['result']
#             return message_id

def escalateL1(watchdogevent):
    if not j.tools.watchdog.manager.inAlert(watchdogevent):
        watchdogevent.escalationstate = 'L1'
        # contact1 = redis_client.hget('contacts', '1')
        message = str(watchdogevent)
        # message_id = _send_message(message, [contact1,])
        # watchdogevent.message_id = message_id
        j.tools.watchdog.manager.setAlert(watchdogevent)
        print "Escalate:%s"%message

def escalateL2(watchdogevent):
    if watchdogevent.escalationstate == 'L1':
        watchdogevent.escalationstate = 'L2'
        contacts = redis_client.hgetall('contacts')
        message = str(watchdogevent)
        message_id = _send_message(message, [contacts['2'], contacts['3']])
        watchdogevent.message_id = message_id
        j.tools.watchdog.manager.setAlert(watchdogevent)
    
def escalateL3(watchdogevent):    
    if watchdogevent.escalationstate == 'L2':
        watchdogevent.escalationstate = 'L3'
        contacts = redis_client.hgetall('contacts')['all'].split(',')
        message = str(watchdogevent)
        message_id = _send_message(message, contacts)
        watchdogevent.message_id = message_id
        j.tools.watchdog.manager.setAlert(watchdogevent)
