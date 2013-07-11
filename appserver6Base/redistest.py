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

ps=r.pubsub()
ps.subscribe([1])


#print "startlisten"
#while True:
    #info=ps.listen()

from pylabs.Shell import ipshellDebug,ipshell
print "DEBUG NOW redistest"
ipshell()


q.application.stop()
