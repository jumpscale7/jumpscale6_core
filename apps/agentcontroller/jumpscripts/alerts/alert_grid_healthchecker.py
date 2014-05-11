
from JumpScale import j

descr = """
Check on grid health
"""

organization = "jumpscale"
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
period = 60*15  # always in sec
startatboot = True
order = 1
enable = True
async = False
log = False
queue ='process'
roles = ['master']


def action():

    if not j.application.config.exists("grid.watchdog.addr") or j.application.config.exists("grid.watchdog.addr")=="":
        return

    import JumpScale.baselib.watchdog.client

    import JumpScale.baselib.redis
    import time
    try:
        import ujson as json
    except:
        import json

    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    results, errors = j.core.grid.healthchecker.runAll()
    results=rediscl.hget('healthcheck:monitoring', 'results')
    errors=rediscl.hget('healthcheck:monitoring', 'errors')
    lastcheck=rediscl.hget('healthcheck:monitoring', 'lastcheck')

    from IPython import embed
    print "Check on grid health"
    embed()
    

    for nid, error in errors:
        j.tools.watchdog.client.send("grid.healthcheck","CRITICAL", -1, nid=nid)
