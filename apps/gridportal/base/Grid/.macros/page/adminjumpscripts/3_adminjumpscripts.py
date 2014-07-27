
try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):
    def _formatdata(jumpscripts):
        aaData = list()
        for name, jumpscript in jumpscripts.iteritems():
            itemdata = ['<a href=adminjumpscript?name=%s>%s</a>' % (name, name)]
            for field in ['organization', 'version', 'descr']: #code
                itemdata.append(str(jumpscript[field]))
            aaData.append(itemdata)
        aaData = str(aaData)
        return aaData.replace('[[', '[ [').replace(']]', '] ]')

    cl=j.clients.redis.getGeventRedisClient("localhost", 7770)

    if not j.application.config.exists("grid.watchdog.secret") or j.application.config.exists("grid.watchdog.secret") == "":
        page = args.page
        page.addMessage('* no grid configured for watchdog: hrd:grid.watchdog.secret')
        params.result = page
        return params

    key = "%s:admin:jscripts" % j.application.config.get("grid.watchdog.secret")
    scripts = cl.hgetall(key)
    jumpscripts = dict([(scripts[i], json.loads(scripts[i+1])) for i, _ in enumerate(scripts) if i % 2 == 0])
    jscripts = _formatdata(jumpscripts)

    try:
        import JumpScale.baselib.watchdog.manager
    except:
        page = args.page
        page.addMessage('* Alerts are not configured')
        params.result = page
        return params

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ('Name', 'Organization', 'Version', 'Description')
    tableid = modifier.addTableFromData(jscripts, fieldnames)

    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
