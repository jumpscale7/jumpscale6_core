from pylabs.InitBase import *
import time

q.application.appname = "testlogger"
q.application.start()

q.logger.setLogTargetLogForwarder()

nr=10000
start=time.time()
print "start perftest for %s"%nr
for i in range(nr):
    q.logger.log(message="this is a log message, with id %s"%i, level=5, category='my.category')

stop=time.time()
nritems=nr/(stop-start)
print "nritems per sec:%s"%nritems

q.application.stop()
