import datetime

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        if tag == 'from' and val:
            filters['from_'] = {'name': 'lastcheck', 'value': j.base.time.getEpochAgo(val), 'eq': 'gte'}
        elif tag == 'to' and val:
            filters['to'] = {'name': 'lastcheck', 'value': j.base.time.getEpochAgo(val), 'eq': 'lte'}
        elif val:
            if j.basetype.integer.checkString(val):
                val = j.basetype.integer.fromString(val)
            filters[tag] = val
    fieldnames = ['Name', 'IP Address', 'Mac Address', 'Last Checked']

    nicstr = '[%(name)s|nic?id=%(guid)s&nic=%(name)s&nid=%(nid)s]'
    fieldids = ['name', 'ipaddr', 'mac', 'lastcheck']
    fieldvalues = [nicstr,'ipaddr','mac',modifier.makeTime]
    tableid = modifier.addTableForModel('system', 'nic', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')


    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
