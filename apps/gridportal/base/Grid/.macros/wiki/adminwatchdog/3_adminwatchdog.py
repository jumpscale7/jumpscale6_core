import JumpScale.baselib.webdis
import json

def main(j, args, params, tags, tasklet):

    name = args.getTag('name')

    if not name:
        out = 'Missing alert param "name"'
        params.result = (out, args.doc)
        return params

    webdisaddr = j.application.config.get('grid.watchdog.addr')
    
    webdiscl = j.clients.webdis.get(webdisaddr, 7779,timeout=1)

    cl=j.clients.redis.getGeventRedisClient("localhost", 7770)

    if not j.application.config.exists("grid.watchdog.secret") or j.application.config.exists("grid.watchdog.secret") == "":
        page = args.page
        page.addMessage('* no grid configured for watchdog: hrd:grid.watchdog.secret')
        params.result = page
        return params

    try:
        import JumpScale.baselib.watchdog.manager
    except:
        page = args.page
        page.addMessage('* Alerts are not configured')
        params.result = page
        return params

    key = "watchdogevents:%s" % j.application.config.get("grid.watchdog.secret")
    watchdog = cl.hget(key, name)
    watchdog = json.loads(watchdog)

    params.result = (watchdog['value'], args.doc)
    return params
    
