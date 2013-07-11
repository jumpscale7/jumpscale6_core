import time


from pprint import pprint
import cProfile
import pstats

from pylabs.InitBase import *

q.application.appname = "redistest"
q.application.start()

q.qshellconfig.interactive=True

def test(name):
    return name

from RedisQueue import RedisQueue
import inspect
import redis

class WorkerClient():
    def __init__(self,name="workers"):
        self.queue = RedisQueue("queue_%s"%name)
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def do(self,function,actorName="",actorMethod="",**args):
        source=inspect.getsource(function)
        md5=q.tools.hash.md5_string(code)


        from pylabs.Shell import ipshellDebug,ipshell
        print "DEBUG NOW "
        ipshell()

wc=WorkerClient()
print wc.do(test)


q.application.stop()
