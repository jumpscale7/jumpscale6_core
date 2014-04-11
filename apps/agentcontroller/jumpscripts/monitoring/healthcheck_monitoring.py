from JumpScale import j

descr = """
Monitor system status
"""

organization = "jumpscale"
name = 'healthcheck_monitoring'
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "monitor.healthcheck"

period = 120 #always in sec
enable = True
async = True
roles = ["*"]

queue = "process"

def action():
    import JumpScale.grid.gridhealthchecker
    import JumpScale.baselib.redis
    import time
    import ujson

    nodeid = j.application.whoAmI.nid
    if nodeid == j.core.grid.healthchecker.masternid:
        rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
        results, errors = j.core.grid.healthchecker.runAll()
        rediscl.hset('healthcheck:monitoring', 'results', ujson.dumps(results))
        rediscl.hset('healthcheck:monitoring', 'errors', ujson.dumps(errors))
        rediscl.hset('healthcheck:monitoring', 'lastcheck', time.time())

        if errors:
            for nid, categories in errors.iteritems():
                for cat, data in categories.iteritems():
                    msg='%s on node %s seems to be having issues' % (cat, nid)
                    print msg
                    # j.events.opserror(msg, 'monitoring')
