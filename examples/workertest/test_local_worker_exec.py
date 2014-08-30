from JumpScale import j

j.application.start('localworkertest')

import JumpScale.baselib.redisworker


def atest(name):
    import time
    print "hallo"
    time.sleep(2)
    return "works"    

print "start job"
result=j.clients.redisworker.execFunction(atest,name="aname",_category="unknown", _organization="unknown",_timeout=60,\
    _queue="io",_log=True,_sync=True)
print "job done"
print result 

job=j.clients.redisworker.execFunction(atest,name="aname",_category="unknown", _organization="unknown",_timeout=60,\
    _queue="io",_log=True,_sync=False)

print job

print "now wait on job"

j.clients.redisworker.waitJob(job)

print "now 2nd time also done"


j.application.stop(0)
