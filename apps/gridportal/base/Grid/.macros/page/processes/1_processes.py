import datetime

def main(j, args, params, tags, tasklet):

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)
    nid = args.getTag('nid')

    filters = dict()
    if nid:
        filters['nid'] = int(nid)
    filters['active'] = True

    fieldids = ["sname", "nid", "jpname", "jpdomain", "epochstart"]
    fieldnames = ['Name', 'Node', 'Process Name', 'Process Domain', 'Start']
    def pidFormat(row, field):
        return '[%s|/grid/process?id=%s]' % (row['sname'] or row['pname'], row['id'])

    def makeTime(row, field):
        return datetime.datetime.fromtimestamp(row[field]).strftime('%m-%d %H:%M:%S')

    nidstr = '[%(nid)s|/grid/node?id=%(nid)s]'
    fieldvalues = [pidFormat, nidstr, 'jpname', 'jpdomain', makeTime]
    tableid = modifier.addTableForModel('system', 'process', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
