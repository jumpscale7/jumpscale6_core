from JumpScale import j

try:
    import ujson as json
except ImportError:
    import json


class AlertClient(object):
    def __init__(self, ip, port):
        import JumpScale.baselib.webdis
        self._ip = ip
        self._port = port
        self._queue = 'queues:alerts'
        self._client = j.clients.webdis.get(ip, port)

    def sendAlert(self, gid, nid, category, state, value, ecoguid=None):
        msg = {'nid': nid,
               'gid': gid,
               'category': category,
               'state': state,
               'ecoguid': ecoguid,
               }
        self._client.rpush(self._queue, json.dumps(msg))

class EventHandler(object):

    def __init__(self):
        self.__aclient = None

    @property
    def _aclient(self):
        if self.__aclient:
            return self.__aclient
        else:
            ip = j.application.config.get('alert.client.ip')
            port = j.application.config.getInt('alert.client.port')
            self.__aclient = AlertClient(ip, port)
            return self.__aclient

    
    def bug_critical(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR:%s\n"%e
        msg+="((C:%s L:1 T:B))"%category
        raise RuntimeError(msg)

    def bug_warning(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR:%s\n"%e
        msg+="((C:%s L:1 T:B))"%category
        j.errorconditionhandler.raiseBug(msg,category=category, pythonExceptionObject=e,die=False)

    def opserror_critical(self,msg,category="",e=None):
        """
        will die
        @param e is python error object when doing except
        """    
        if e<>None:
            msg+="\nERROR:%s\n"%e
        msg+="((C:%s L:1 T:O))"%category
        raise RuntimeError(msg)

    def opserror(self,msg,category="",e=None):
        """
        will NOT die
        @param e is python error object when doing except
        """        
        if e<>None:
            msg+="\nERROR:%s\n"%e
        j.errorconditionhandler.raiseOperationalCritical(msg,category=category,die=False)

    def raiseAlert(self, category, state, value=None, ecoguid=None, gid=None, nid=None):
        gid = gid or j.application.whoAmI.gid
        nid = nid or j.application.whoAmI.nid
        self._aclient.sendAlert(gid, nid, category, state, value, ecoguid)

