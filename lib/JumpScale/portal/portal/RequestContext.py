import re

REC = re.compile("(?P<code>\d+)\s+(?P<message>.*)")

class RequestContext(object):

    """
    is context of one request to WS
    please keep this as light as possible because these objects are mostly created
    """

    def __init__(self, application, actor, method, env, start_response, path, params={}, fformat=""):
        self.env = env
        self._start_response = start_response
        if params == "":
            params = {}
        self.params = params
        self.path = path
        self.actor = actor
        self.application = application
        self.method = method
        self._response_started = False
        self.httpStatus = 200
        self.httpMessage = "OK"
        self.fformat = fformat.strip().lower()

    def start_response(self, status, *args, **kwargs):
        if self._response_started:
            print 'RESPONSE Already started ignoring'
            return
        self._response_started = True
        statusm = REC.match(status)
        if statusm:
            self.httpStatus = int(statusm.group('code'))
            self.httpMessage = statusm.group('message')
        self.status = status
        if '_jsonp' in self.params:
            status = '200 OK'
        return self._start_response(status, *args, **kwargs)

    def checkFormat(self):
        if self.fformat == "" or self.fformat == None:
            self.fformat = "json"
        if self.fformat not in ["human", "json", "jsonraw", "text", "html", "raw"]:
            return False
        return True
