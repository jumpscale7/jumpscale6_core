from JumpScale import j


from redis import Redis
from rq import Queue
j.application.start("reload")


redis = Redis("127.0.0.1", 7768, password=None)

q = Queue(name="testqueue",connection=redis)

from testf import *

for i in range(10):
    result = q.enqueue(testf, 'test', timeout=600)



j.application.stop()