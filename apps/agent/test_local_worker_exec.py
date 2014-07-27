from JumpScale import j

j.application.start('localworkertest')

import JumpScale.baselib.redisworker

def atest(name,prio):
    print "hallo"
    return "works"    

result=j.clients.redisworker.execFunction(atest,name="aname",_category="unknown", _organization="unknown",_timeout=60,_queue="io",_log=True,_sync=True)
print result 

job=j.clients.redisworker.execFunction(atest,name="aname",_category="unknown", _organization="unknown",_timeout=60,_queue="io",_log=True,_sync=False)

print job

from IPython import embed
print "main"
embed()



j.application.stop(0)
