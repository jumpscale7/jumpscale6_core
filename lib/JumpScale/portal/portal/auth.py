from JumpScale import j
import JumpScale.grid.osis
import ujson as json

class auth(object):
    clients = dict()

    def __init__(self, groups, audit=True):
        if isinstance(groups, basestring):
            groups = [groups]
        self.groups = set(groups)
        self.audit = audit


    def getClient(self, namespace):
        client = self.clients.get(namespace)
        if not client:
            client = j.core.osis.getClientForNamespace(namespace)
            self.clients[namespace] = client
        return client

    def doAudit(self, user, statuscode, pathinfo, args, kwargs, result):
        client = self.getClient('system')
        audit = client.audit.new()
        audit.user = user
        audit.call = pathinfo
        audit.statuscode = statuscode
        audit.args = json.dumps(args[1:]) # we dont want to log self
        auditkwargs = kwargs.copy()
        auditkwargs.pop('ctx')
        audit.kwargs = json.dumps(auditkwargs)
        audit.result = json.dumps(result)
        client.audit.set(audit)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            ctx = kwargs['ctx']
            user = ctx.env['beaker.session']['user']
            pathinfo = ctx.env['PATH_INFO']
            result = None
            resultcalled = False
            statuscode = None
            if self.groups:
                userobj = j.core.portal.active.auth.getUserInfo(user)
                groups = set(userobj.groups)
                if not groups.intersection(self.groups):
                    self.doAudit(user, 403, pathinfo, args, kwargs, {})
                    ctx.start_response('403 Forbidden', [])
                    return 'User %s has no access. If you would like to gain access please contact your adminstrator' % user
            if self.audit:
                start_response = ctx.start_response
                def patched_start_response(status, *pargs, **pkwargs):
                    statuscode = int(status[0:3])
                    if resultcalled:
                        self.doAudit(user, statuscode, pathinfo, args, kwargs, result)
                    return start_response(status, *pargs, **pkwargs)
                ctx.start_response = patched_start_response
            try:
                result = func(*args, **kwargs)
                resultcalled = True
                return result
            finally:
                if self.audit and statuscode:
                    self.doAudit(user, statuscode, pathinfo, args, kwargs, result)
        return wrapper

