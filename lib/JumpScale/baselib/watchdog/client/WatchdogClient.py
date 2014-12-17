from JumpScale import j
import JumpScale.baselib.watchdog as watchdog

try:
    import ujson as json
except:
    import json


class WatchdogClient:
    def __init__(self):
        # addr = j.application.config.get("grid.watchdog.addr", default=False)
        # if not addr:
        #     raise RuntimeError("please configure grid.watchdog.addr in hrdconfig")
        # secret = j.application.config.get("grid.watchdog.secret", default=False)
        # if not secret:
        #     raise RuntimeError("please configure grid.watchdog.secret in hrdconfig")
        # self.secret = secret
        self.rediscl = j.clients.redis.getByInstanceName('system')

    def _setWatchdogEvent(self, alert, pprint=False):
        res=self.rediscl.hset(watchdog.getHSetKey(alert.gid), "%s_%s" % (alert.nid, alert.category), alert)
        if pprint:
            print alert
        return res

    def send(self, alert, pprint=False):
        return self._setWatchdogEvent(alert, pprint=pprint)


