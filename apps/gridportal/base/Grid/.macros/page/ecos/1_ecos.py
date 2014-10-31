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
            if j.basetype.integer.checkString(val):
                val = j.basetype.integer.fromString(val)
            filters[tag] = val
    fieldnames = ['Time', 'Grid ID', 'Node ID', 'App Name', 'Category', 'Error Message', 'Job ID']

    def errormessage(row, field):
        return row[field].replace('\n', '<br>')

    def makeTime(row, field):
        time = datetime.datetime.fromtimestamp(row[field]).strftime('%m-%d %H:%M:%S') or ''
        return '[%s|eco?id=%s]' % (time, row['guid'])

    def makeJob(row, field):
        jid = row[field]
        return '[%s|job?id=%s]' % (jid, jid) if (not jid == 0) else 'N/A'


    nidstr = '[%(nid)s|node?id=%(nid)s&gid=%(gid)s]'

    fieldids = ["epoch", "gid", "nid", "appname", "category", "errormessage", "jid"]
    fieldvalues = [makeTime, 'gid', nidstr, 'appname', 'category', errormessage, makeJob]
    tableid = modifier.addTableForModel('system', 'eco', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')


    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
