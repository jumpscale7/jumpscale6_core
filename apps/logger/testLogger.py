from JumpScale import j
import JumpScale.grid
import time

j.application.start("testlogger")

j.logger.addLogTargetElasticSearch()

nr = 10000
start = time.time()
print "start perftest for %s" % nr
for i in range(nr):
    j.logger.log(message="this is a log message, with id %s" % i, level=5, category='my.category')

stop = time.time()
nritems = nr / (stop - start)
print "nritems per sec:%s" % nritems

j.application.stop()
