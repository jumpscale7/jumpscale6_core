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
        self.fformat = fformat.strip().lower()

    def start_response(self, *args, **kwargs):
        if self._response_started:
            print 'RESPONSE Already started ignoring'
            return
        self._response_started = True
        return self._start_response(*args, **kwargs)

    def checkFormat(self):
        if self.fformat == "" or self.fformat == None:
            self.fformat = "json"
        if self.fformat not in ["human", "json", "jsonraw", "text", "html", "raw"]:
            return False
        return True