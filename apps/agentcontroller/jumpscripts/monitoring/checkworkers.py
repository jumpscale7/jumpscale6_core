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
    for workername in redis.hkeys("workers:watchdog"):
        last=redis.hget("workers:watchdog",workername)
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
        for proc in psutil.process_iter():
            name2=" ".join(proc.cmdline)
            # print "**%s"%name2

            if name2.find("python worker.py")<>-1:
                workernamefound=name2.split("-wn")[-1].strip()
                if workernamefound in workerstimeout:
                    workerstimeout.pop(workerstimeout.index(workernamefound))

        for workername in workerstimeout:
            j.tools.startupmanager.startProcess("workers",workername)

    except Exception,e:
        print "ERROR IN MONITORING & TRYING TO RESTART WORKERS, error:\n%s"%e



