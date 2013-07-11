import time

from pprint import pprint
import cProfile
import pstats

from pylabs.InitBase import *

q.application.appname = "redistest"
q.application.start()

q.qshellconfig.interactive=True

import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

print "start send"
for i in range(10000):
    r.publish(1, "a test")



q.application.stop()
