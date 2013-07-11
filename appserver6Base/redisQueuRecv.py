import time

from pprint import pprint
import cProfile
import pstats

from pylabs.InitBase import *

q.application.appname = "redistest"
q.application.start()

q.qshellconfig.interactive=True

#import redis
#r = redis.StrictRedis(host='localhost', port=6379, db=0)

from RedisQueue import RedisQueue
q = RedisQueue('test')

q = RedisQueue('test')

print "start recv"
while True:
    res=float(q.get())
    if int(res)==int(round(res/1000,0)*1000):
        print res



q.application.stop()
