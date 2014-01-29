import datetime

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        if tag == 'from' and val:
            filters['from_'] = {'name': 'epoch', 'value': j.base.time.getEpochAgo(val), 'eq': 'gte'}
        elif tag == 'to' and val:
            filters['to'] = {'name': 'epoch', 'value': j.base.time.getEpochAgo(val), 'eq': 'lte'}
        elif val:
            filters[tag] = val
    fieldnames = ["Time", 'Node ID', 'App Name', 'Category', 'Error Message', 'Job ID']

    def errormessage(row, field):
        return row[field].replace('\n', '<br>')

    def makeTime(row, field):
        time = datetime.datetime.fromtimestamp(row[field]).strftime('%m-%d %H:%M:%S') or ''
        return '[%s|eco?id=%s]' % (time, row['guid'])

    nidstr = '[%(nid)s|node?id=%(nid)s]'
    jidstr = '[%(jid)s|job?id=%(jid)s]'

    fieldids = ["epoch", "nid", "appname", "category", "errormessage", "jid"]
    fieldvalues = [makeTime, nidstr, 'appname', 'category', errormessage, jidstr]
    tableid = modifier.addTableForModel('system', 'eco', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
