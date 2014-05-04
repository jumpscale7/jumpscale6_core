
from JumpScale import j

descr = """
remove old redis cache from system
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "redis.cleanup"
period = 300  # always in sec
order = 1
enable = True
async = True
log = False
roles = ['master']


def action():
    import time
    EXTRATIME = 120
    now = time.time()
    try:
        import ujson as json
    except:
        import json
    ocl = j.core.osis.getClient(user='root')
    jcl = j.core.osis.getClientForCategory(ocl, 'system', 'job')
    rcl = j.clients.redis.getRedisClient('127.0.0.1', 7769)
    jobkey = 'jobs:%s' % j.application.whoAmI.gid
    jobs = rcl.hgetall(jobkey)
    for jobguid, jobstring in jobs.iteritems():
        job = json.loads(jobstring)
        if job['state'] in ['OK', 'ERROR', 'TIMEOUT']:
            rcl.hdel(jobkey, jobguid)
        elif job['timeStart'] + job['timeout'] + EXTRATIME < now:
            rcl.hdel(jobkey, jobguid)
            job['state'] = 'TIMEOUT'
            eco = j.errorconditionhandler.getErrorConditionObject(msg='Job timed out')
            j.errorconditionhandler.raiseOperationalCritical(eco=eco,die=False)
            eco.tb = None
            eco.type = str(eco.type)
            job['result'] = json.dumps(eco.__dict__)
            jcl.set(job)

