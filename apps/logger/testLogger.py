from OpenWizzy import o
import OpenWizzy.grid
import time

o.application.appname = "testlogger"
o.application.start()

o.logger.addLogTargetElasticSearch()

nr=10000
start=time.time()
print "start perftest for %s"%nr
for i in range(nr):
    o.logger.log(message="this is a log message, with id %s"%i, level=5, category='my.category')

stop=time.time()
nritems=nr/(stop-start)
print "nritems per sec:%s"%nritems

o.application.stop()
