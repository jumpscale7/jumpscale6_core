
from JumpScale import j

descr = """
remove old redis cache from system
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "redis.cleanup"
period = 7200  # always in sec
order = 1
enable = True
async = True
log = False



def action():
    import time
    EXTRATIME = 120
    now = time.time()
    import ujson
    masterip = j.application.config.get('grid.master.ip')
    if j.system.net.isIpLocal(masterip):
        rcl = j.clients.redis.getRedisClient('127.0.0.1', 7769)
        jobkey = 'jobs:%s' % j.application.whoAmI.gid
        jobs = rcl.hgetall(jobkey)
        for jobguid, jobstring in jobs.iteritems():
            job = ujson.loads(jobstring)
            if job['timeStart'] + job['timeout'] + EXTRATIME < now:
                rcl.hdel(jobkey, jobguid)
