
from JumpScale import j
import time

j.application.start("lrucache")

j.logger.consoleloglevel = 6

import JumpScale.baselib.lrucache


def test(obj):
    print "writecachedobject:%s" % obj

cache = j.db.cache.getRWCache(nrItemsReadCache=10, nrItemsWriteCache=10000, maxTimeWriteCache=5, writermethod=test)

# after 5 sec cache should start to empty
t = 0
for i in range(10000):
    cache.set(i, "aPieceOfContent%s" % i)
    time.sleep(0.1)
    t += 1
    if t > 10:
        t = 0
        cache.flush()  # flush needs to be requested on regular intervals


cache.flush()

# from IPython import embed
# print "main shell"
# embed()

j.application.stop()
