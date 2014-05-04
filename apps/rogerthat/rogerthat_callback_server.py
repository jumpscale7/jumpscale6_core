#! /usr/bin/python
from gevent.pywsgi import WSGIServer
from JumpScale import j
import JumpScale.baselib.redis
import time
import JumpScale.lib.rogerthat

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

    def process_update(self, status, answer_id, received_timestamp, member, user_details, message_key, parent_message_key, tag, acked_timestamp, service_identity, result_key):
        if status == 3:
            message_data_json = self.redis_client.hget('messages', message_key)
            if message_data_json:
                message_data = json.loads(message_data_json)
                if message_data['state'] == 'L1':
                    epoch = time.time()
                    message_data['epoch'] = epoch
                    message_data['state'] = 'C'
                    message_data['log'] = '%s: %s %s' % (epoch, user_details['email'], 'C')
                    self.redis_client.hset('messages', message_key, message_data)
                    answers = [{'id': 'yes', 'caption': 'Accept', 'action': '', 'type': 'button'},]
                    self.send_message(message_data['message'], user_details['email'], answers, message_key)
                    return None
                elif message_data['state'] == 'C':
                    epoch = time.time()
                    message_data['epoch'] = epoch
                    message_data['state'] = 'A'
                    message_data['log'] = '%s: %s %s' % (epoch, user_details['email'], 'C')
                    self.redis_client.hset('messages', message_key, message_data)
                    answers = [{'id': 'yes', 'caption': 'Resolve', 'action': '', 'type': 'button'},]
                    self.send_message(message_data['message'], user_details['email'], answers, message_key)
                    return None
                elif message_data['state'] == 'A':
                    epoch = time.time()
                    message_data['epoch'] = epoch
                    message_data['state'] = 'R'
                    message_data['log'] = '%s: %s %s' % (epoch, user_details['email'], 'C')
                    self.redis_client.hset('messages', message_key, message_data)
                    answers = [{'id': 'yes', 'caption': 'Close', 'action': '', 'type': 'button'},]
                    self.send_message(message_data['message'], user_details['email'], answers, message_key)
                    return None
                elif message_data['state'] == 'R':
                    epoch = time.time()
                    message_data['epoch'] = epoch
                    message_data['state'] = 'Z'
                    message_data['log'] = '%s: %s %s' % (epoch, user_details['email'], 'C')
                    self.redis_client.hset('messages', message_key, message_data)
                    return None

    def start(self):
        print 'started on %s' % self.port
        self.server.serve_forever()

GeventWSServer('0.0.0.0', 5005).start()