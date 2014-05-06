#! /usr/bin/python
from JumpScale import j
from gevent.pywsgi import WSGIServer
import JumpScale.baselib.redis
import time
import JumpScale.lib.rogerthat
import JumpScale.baselib.watchdog.manager

try:
    import ujson as json
except ImportError:
    import json

def jsonrpc(func):
    def wrapper(s, environ, start_response):
        if not environ["REQUEST_METHOD"]=='POST':
            return s.invalidRequest()

        service_key = environ['HTTP_X_NUNTIUZ_SERVICE_KEY']
        if not s._authenticateRequest(service_key):
           return s.invalidRequest()

        data = environ['wsgi.input'].read()
        msg = dict()
        try:
            msg = json.loads(data)
        except Exception, e:
            print e
            result = s.invalidRequest()

        if msg:
            try:
                data = func(s, msg['method'], **msg['params'])
                result = {'result': data, 'id': msg['id'], 'error': None}
            except Exception, e:
                print e
                result = s.invalidRequest()

        statuscode = '500 Internal Server Error' if result.get('error') else '200 OK'
        result = json.dumps(result)
        start_response(statuscode, (('Content-type', 'application/json-rpc'),))
        return result
    return wrapper

class GeventWSServer(object):

    def __init__(self, addr, port):
        self.port = port
        self.addr = addr
        self.redis_port = int(j.application.config.get('redis.alerts.port', default=6379))
        self.redis_client = j.clients.credis.getRedisClient('127.0.0.1', self.redis_port)
        self.api_key = j.application.config.get('rogerthat.apikey')
        self.rogerthat_client = j.clients.rogerthat.get(self.api_key)
        self.server = WSGIServer((self.addr, self.port), self.rpcRequest)
        
    def invalidRequest(self):
        msg = {'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None, 'jsonrpc': '2.0'}
        return msg

    def _authenticateRequest(self, service_key):
        return service_key == j.application.config.get('rogerthat.servicekey')
        
    @jsonrpc
    def rpcRequest(self, method, **params):
        if method == 'test.test':
            return self.process_test(**params)

        elif method == 'messaging.update':
            return self.process_update(**params)

    def process_test(self, value):
        return value

    def send_message(self, message, contacts, answers, parent_message_key, alert_flags=6):
        result = self.rogerthat_client.send_message(message, contacts, answers=answers, alert_flags=alert_flags, parent_message_key=parent_message_key)
        if result:
            if result['error']:
                j.logger.log('Could not send rogerthat message')
                return
            else:
                message_id = result['result']
                return message_id

    def process_update(self, status=None, answer_id=None, received_timestamp=None, member=None, user_details=None, message_key=None, parent_message_key=None, tag=None, acked_timestamp=None, service_identity=None, result_key=None):
        message_key = parent_message_key if parent_message_key else message_key

        alert = None
        for al in j.tools.watchdog.manager.fetchAllAlerts():
            if al['message_id'] == message_key:
                alert = al

        if alert:
            if alert['escalationstate'] == 'L1' and answer_id == 'yes':
                wde = j.tools.watchdog.manager.getWatchdogEvent(alert['gguid'], alert['nid'], alert['category'])
                wde.escalationstate = 'C'
                wde.escalationepoch = time.time()
                j.tools.watchdog.manager.setWatchdogEvent(wde)
                answers = [{'id': 'yes', 'caption': 'Accept', 'action': '', 'type': 'button'},]
                self.send_message(str(wde), [member,], answers, message_key)
                return None
            elif alert['escalationstate'] == 'C' and answer_id == 'yes':
                wde = j.tools.watchdog.manager.getWatchdogEvent(alert['gguid'], alert['nid'], alert['category'])
                wde.escalationstate = 'A'
                wde.escalationepoch = time.time()
                j.tools.watchdog.manager.setWatchdogEvent(wde)
                answers = [{'id': 'yes', 'caption': 'Resolve', 'action': '', 'type': 'button'},]
                self.send_message(str(wde), [member,], answers, message_key)
                return None
            elif alert['escalationstate'] == 'A' and answer_id == 'yes':
                wde = j.tools.watchdog.manager.getWatchdogEvent(alert['gguid'], alert['nid'], alert['category'])
                wde.escalationstate = 'R'
                wde.escalationepoch = time.time()
                j.tools.watchdog.manager.setWatchdogEvent(wde)
                answers = [{'id': 'yes', 'caption': 'Close', 'action': '', 'type': 'button'},]
                self.send_message(str(wde), [member,], answers, message_key)
                return None
            elif alert['escalationstate'] == 'R' and answer_id == 'yes':
                wde = j.tools.watchdog.manager.getWatchdogEvent(alert['gguid'], alert['nid'], alert['category'])
                j.tools.watchdog.manager.deleteAlert(wde)
                return None

    def start(self):
        print 'started on %s' % self.port
        self.server.serve_forever()

GeventWSServer('0.0.0.0', 5005).start()