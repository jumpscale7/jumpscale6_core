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

print "start send"
for i in range(100000):
    q.put(i)

#q.application.stop()
