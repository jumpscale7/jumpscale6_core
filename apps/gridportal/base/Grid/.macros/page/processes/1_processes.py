import datetime

def main(j, args, params, tags, tasklet):

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)
    nid = args.getTag('nid')

    filters = dict()
    if nid:
        filters['nid'] = nid

    fieldids = ["systempids", "nid", "sname", "jpname", "jpdomain", "epochstart", "active"]
    fieldnames = ['Pids', 'Node', 'Name', 'Process Name', 'Process Domain', 'Start', 'Active']
    def pidFormat(row, field):
        pids = ', '.join([ str(x) for x in row[field]])
        return '[%s|/grid/process?id=%s]' % (pids, row['id'])

    def makeTime(row, field):
        return datetime.datetime.fromtimestamp(row[field]).strftime('%m-%d %H:%M:%S')

    nidstr = '[%(nid)s|/grid/node?id=%(nid)s]'
    fieldvalues = [pidFormat, nidstr, 'sname', 'jpname', 'jpdomain', makeTime, 'active']
    modifier.addTableForModel('system', 'process', fieldids, fieldnames, fieldvalues, filters)
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
