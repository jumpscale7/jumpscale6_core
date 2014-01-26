import datetime

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.getDict().iteritems():
        val = args.getTag(tag)
        if tag == 'from' and val:
            filters[tag] = j.base.time.getEpochAgo(val)
        elif val:
            filters[tag] = val

    fieldnames = ['App Name', 'Category', 'Start Time', 'Message', 'Level', 'Process ID', 'Node ID', 'Job ID']

    def makeTime(row, field):
        return datetime.datetime.fromtimestamp(row[field]).strftime('%m-%d %H:%M:%S') or ''

    appstr = '[%(appname)s|/grid/log?id=%(id)s]'
    nidstr = '[%(nid)s|/grid/node?id=%(nid)s]'
    pidstr = '[%(pid)s|/grid/process?id=%(pid)s]'
    jidstr = '[%(jid)s|/grid/job?id=%(jid)s]'
    fieldids = ['appname', 'category', 'epoch', 'message', 'level', 'pid', 'nid', 'jid']
    fieldvalues = [appstr, 'category', makeTime, 'message', 'level', pidstr, nidstr, jidstr]
    tableid = modifier.addTableForModel('system', 'log', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
