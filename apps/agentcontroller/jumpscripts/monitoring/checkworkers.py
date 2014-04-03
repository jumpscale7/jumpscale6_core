from JumpScale import j

descr = """
check if workers are running
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "system.checkworkers"
period = 5
enable=True
startatboot=False
async=False
log=False
roles = ["*"]



def action():
    import JumpScale.baselib.redis
    import time

    redis = j.clients.redis.getGeventRedisClient("127.0.0.1", 7768)

    workers2 = redis.hgetall("workers:watchdog")
    foundworkers={}
    for workername, timeout in zip(workers2[0::2], workers2[1::2]):    
        foundworkers[workername]=timeout

    nrworkersrequired=len(foundworkers.keys())

    j.system.process.checkstart("jpackage start -n workers","worker.py",nrworkersrequired,retry=3)





