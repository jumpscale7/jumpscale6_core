import datetime

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ['Node ID', 'App Name', 'Category', 'Error Message', 'Job ID', "Time"]
    filters = dict()

    def errormessage(row, field):
        return row[field].replace('\n', '<br>')

    def makeTime(row, field):
        time = datetime.datetime.fromtimestamp(row[field]).strftime('%m-%d %H:%M:%S') or ''
        return '[%s|grid/eco?id=%s]' % (time, row['guid'])

    nidstr = '[%(nid)s|/grid/node?id=%(nid)s]'
    jidstr = '[%(jid)s|/grid/job?id=%(jid)s]'

    fieldids = ["nid", "appname", "category", "errormessage", "jid", "epoch"]
    fieldvalues = [nidstr, 'appname', 'category', errormessage, jidstr, makeTime]
    tableid = modifier.addTableForModel('system', 'eco', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
