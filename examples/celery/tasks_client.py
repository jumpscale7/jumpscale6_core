# import sys
# sys.path.append("lib")

from JumpScale import j
import JumpScale.baselib.celery

j.application.start('celery:tasks:client')


test=j.clients.celery.celeryClient("test",url="redis://localhost:9999/0",actorsPath="actors")
result= test.add.delay(4, 4).get()

print result

test2=j.clients.celery.celeryClient("test2",url="redis://localhost:9999/0",actorsPath="actors")
result= test2.add.delay(4, 4).get()

print result

j.application.stop()
