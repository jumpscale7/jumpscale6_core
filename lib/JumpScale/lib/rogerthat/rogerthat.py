from JumpScale import j
import ujson
import urllib2

class RogerthatFactory(object):

    def get(self, api_key):
        return Rogerthat(api_key)

class Rogerthat(object):

    def __init__(self, api_key):
        self._api_key = api_key
        self._url = 'https://rogerth.at/api/1'

    def _raw_request(self, method, params):
        data = {'id': j.base.idgenerator.generateGUID(), 'method': method, 'params': params}
        json_data = ujson.dumps(data)
        headers = {'Content-Type': 'application/json-rpc; charset=utf-8', 'X-Nuntiuz-API-key': self._api_key}
        request = urllib2.Request(self._url, json_data, headers)
        response = urllib2.urlopen(request)
        if response.getcode() == 200:
            result = ujson.loads(response.read())
            return result
        else:
            j.logger.log('Server error when executing send_message')
            return False


    def send_message(self, message, members=None, flags=0, parent_message_key=None, answers=None, dismiss_button_ui_flags=0, alert_flags=0, branding=None, tag=None, context=None):
        members = members or list()
        answers = answers or list()
        params = {'message': message, 'members': members, 'flags': flags}
        params['parent_message_key'] = parent_message_key
        params['answers'] = answers or []
        params['dismiss_button_ui_flags'] = dismiss_button_ui_flags
        params['alert_flags'] = alert_flags
        params['branding'] = branding
        params['tag'] = tag
        params['context'] = context
        return self._raw_request('messaging.send', params)


    def send_broadcast(self, broadcast_type, message, flags=0, parent_message_key=None, answers=None, dismiss_button_ui_flags=0, alert_flags=0, branding=None, tag=None, context=None):
        params = {'message': message, 'flags': flags}
        params['parent_message_key'] = parent_message_key
        params['answers'] = answers or []
        params['dismiss_button_ui_flags'] = dismiss_button_ui_flags
        params['alert_flags'] = alert_flags
        params['branding'] = branding
        params['tag'] = tag
        params['context'] = context
        params['broadcast_type'] = broadcast_type
        return self._raw_request('messaging.broadcast', params)


    def retreive_users(self):
        params = {'service_identity': '+default+', 'cursor': None}
        friends = list()
        while True:
            results = self._raw_request('friend.list', params)['result']
            friends.extend(results['friends'])
            if results['friends'] and results['cursor']:
                params['cursor'] = results['cursor']
            else:
                break

        return friends
