#! /usr/bin/python
from JumpScale import j
import JumpScale.baselib.redis
import JumpScale.lib.rogerthat

try:
    import ujson as json
except ImportError:
    import json
import time
import gevent

j.application.start("alerts_server")

API_KEY = j.application.config.get('rogerthat.apikey')

redis_client = j.clients.redis.getByInstanceName('system')
alerts_queue = redis_client.getQueue('alerts')
rogerthat_client = j.clients.rogerthat.get(API_KEY)

ANSWERS = [{'id': 'yes', 'caption': 'Take', 'action': '', 'type': 'button'},]

def send_message(message, contacts, answers=ANSWERS, alert_flags=6):
    result = rogerthat_client.send_message(message, contacts, answers=answers, alert_flags=alert_flags)
    if result:
        if result['error']:
            j.logger.log('Could not send rogerthat message')
            return
        else:
            message_id = result['result']
            return message_id

def escalate_L1(message):
    # hash 'contacts' contains keys 1, 2, 3 and all with rogerthat ids
    contact1 = redis_client.hget('contacts', '1')
    contacts = [contact1,]
    message_id = send_message(message, contacts)
    epoch = time.time()
    message_data = {"epoch": epoch, "state": 'L1', "log": '%s: %s %s' % (epoch, ', '.join(contacts), 'L1'), "message": message}
    redis_client.hset('messages', message_id, ujson.dumps(message_data))
    return message_id

def escalate_L2(message, message_id):
    message_data = json.loads(redis_client.hget('messages', message_id))
    if message_data['state'] == 'L1':
        # hash 'contacts' contains keys 1, 2, 3 and all with rogerthat ids
        contact2 = redis_client.hget('contacts', '2')
        contact3 = redis_client.hget('contacts', '3')
        contacts = [contact2, contact3]
        send_message(message, contacts)
        epoch = time.time()
        message_data = {'epoch': epoch, 'state': 'L2', 'log': '%s: %s %s' % (epoch, ', '.join(contacts), 'L2'), 'message': message}
        redis_client.hset('messages', message_id, ujson.dumps(message_data))

def escalate_L3(message, message_id):
    message_data = json.loads(redis_client.hget('messages', message_id))
    if message_data['state'] == 'L2':
        # hash 'contacts' contains keys 1, 2, 3 and all with rogerthat ids
        contacts = json.loads(redis_client.hget('contacts', 'all'))
        send_message(message, contacts)
        epoch = time.time()
        message_data = {'epoch': epoch, 'state': 'L3', 'log': '%s: %s %s' % (epoch, ', '.join(contacts), 'L3'), 'message': message}
        redis_client.hset('messages', message_id, ujson.dumps(message_data))

while True:
    alert_json = alerts_queue.get()
    alert = json.loads(alert_json)
    if alert['state'] == 'CRITICAL':
        # escalate L1
        message_id = escalate_L1(alert['errormessage'])

        # escalate L2 after 5 mins
        #gevent.spawn_later(escalate_L2, 300.0, message=message, message_id=message_id)

        # escalate L3 after 15 mins
        #gevent.spawn_later(escalate_L3, 1200.0, message=message, message_id=message_id)


j.application.stop()
