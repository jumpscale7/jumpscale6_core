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
    workerstimeout=[]
    now=time.time()
    workers = redis.hgetall("workers:watchdog")
    for workername, last in zip(workers[0::2], workers[1::2]):
        if last==None or now>int(last)+10:
            #timeout on watchdog
            workerstimeout.append(workername)

        elif now>int(last)+7200:
            #timeout on watchdog
            j.tools.startupmanager.restartProcess("workers",workername)

    if workerstimeout==[]:
        return

    try:
        import psutil
        foundworkers=[]
        for timeout in workerstimeout[:]:
            if j.tools.startupmanager.getStatus('workers', timeout):
                workerstimeout.remove(timeout)

        for workername in workerstimeout:
            j.tools.startupmanager.startProcess("workers",workername)

    except Exception,e:
        print "ERROR IN MONITORING & TRYING TO RESTART WORKERS, error:\n%s"%e



