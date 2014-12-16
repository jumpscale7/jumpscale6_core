import datetime

def main(j, args, params, tags, tasklet):
    try:
        import ujson as json
    except:
        import json

    page = args.page

    filters = dict()
    fieldids = ['timestamp', 'user', 'call', 'statuscode']
    for tag, val in args.tags.tags.iteritems():
        if tag in fieldids:
            val = args.getTag(tag)
            filters[tag] = val

    modifier = j.html.getPageModifierGridDataTables(page)

    def makeTime(row, field):
        time = modifier.makeTime(row, field)
        link = "[%s|audit?id=%s]" % (time, row['guid'])
        return link

    fieldnames = ['Time', 'User', 'Call', 'Status Code']
    fieldvalues = [makeTime, 'user', 'call', 'statuscode']
    tableid = modifier.addTableForModel('system', 'audit', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
