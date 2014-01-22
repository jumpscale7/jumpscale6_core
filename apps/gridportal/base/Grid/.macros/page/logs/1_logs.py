import datetime

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ['App Name', 'Category', 'Start Time', 'Message', 'Level', 'Process ID', 'Node ID', 'Job ID']

    def makeTime(row, field):
        return datetime.datetime.fromtimestamp(row[field]).strftime('%m-%d %H:%M:%S') or ''

    appstr = '[%(appname)s|/grid/log?id=%(id)s]'
    nidstr = '[%(nid)s|/grid/node?id=%(nid)s]'
    pidstr = '[%(pid)s|/grid/process?id=%(pid)s]'
    jidstr = '[%(jid)s|/grid/job?id=%(jid)s]'
    fieldids = ['appname', 'category', 'epoch', 'message', 'level', 'pid', 'nid', 'jid']
    fieldvalues = [appstr, 'category', makeTime, 'message', 'level', pidstr, nidstr, jidstr]
    modifier.addTableForModel('system', 'log', fieldids, fieldnames, fieldvalues)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
