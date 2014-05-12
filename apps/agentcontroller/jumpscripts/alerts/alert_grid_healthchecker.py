
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
async = True
log = False
queue ='process'
roles = ['master']


def action():

    import time

    if not j.application.config.exists("grid.watchdog.addr") or j.application.config.exists("grid.watchdog.addr")=="":
        return

    import JumpScale.baselib.redis
    import time
    try:
        import ujson as json
    except:
        import json

    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    # results, errors = j.core.grid.healthchecker.runAll()

    for item in ['results','errors','lastcheck']:
        if not rediscl.hexists('healthcheck:monitoring',item):
            if not j.core.processmanager.checkStartupOlderThan(60*4):
                #can be the healthchecker did not finish yet, lets skip this round
                return

    check=True
    if not rediscl.hexists('healthcheck:monitoring','lastcheck'):
        check=False
    else:
        last=int(float(rediscl.hget('healthcheck:monitoring', 'lastcheck')))
        if last<int(time.time())-4*60:
            if not j.core.processmanager.checkStartupOlderThan(60*4):
                return
            check=False

    if check==False:
        j.tools.watchdog.client.send("grid.healthcheck","CRITICAL", gid=j.application.whoAmI.gid, nid=j.application.whoAmI.nid,value="watchdog check did not run in time.")

    results=json.loads(rediscl.hget('healthcheck:monitoring', 'results'))
    errors=json.loads(rediscl.hget('healthcheck:monitoring', 'errors'))
    lastcheck=json.loads(rediscl.hget('healthcheck:monitoring', 'lastcheck'))
    
    import JumpScale.baselib.watchdog.client


    colormap = {'RUNNING': 'green', 'HALTED': 'red', 'UNKOWN': 'orange',
                'BROKEN': 'red', 'OK': 'green', 'NOT OK': 'red'}

    out=""
    for nid, error in errors.iteritems():
        out+="\nh3. Node %s\n" % nid
        for category, msg in error.iteritems():
            if isinstance(msg, list):
                for err in msg:
                    if isinstance(err, dict):
                        out += "|*%s*| | |\n" % (category)
                        for k, v in err.iteritems():
                            v = v.replace('\n', '')
                            for status, color in colormap.iteritems():
                                v = v.replace(status, '{color:%s}*%s*{color}' % (color, status))
                            out += "||%s|%s|\n" % (k,v)
                    else:
                        out += "|*%s*|%s||\n" % (category, err)

    state = "CRITICAL" if errors else "OK"
    j.tools.watchdog.client.send("grid.healthcheck", state, gid=j.application.whoAmI.gid, nid=j.application.whoAmI.nid, value=out, pprint=True)
