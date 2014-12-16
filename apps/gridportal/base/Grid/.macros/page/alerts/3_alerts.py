
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    def makeLink(alert, field):
        link = '<a href=alert?guid=%s>%s</a>' % (alert['guid'], alert['id'])
        return link

    def makeGrid(alert, field):
        return '<a href=grid?id=%s>%s</a>' % (alert['gid'], alert['gid'])

    def makeNode(alert, field):
        return '<a href=node?id=%s&gid=%s>%s</a>' % (alert['nid'], alert['nid'], alert['gid'])


    fieldnames = ('Link to Alert', 'Grid ID', 'Node ID', 'Category', 'Raise Time','Last Time', 'Close Time', 'State', 'Value')
    fieldids = ['id', 'gid', 'nid', 'category', 'inittime', 'lasttime', 'closetime', 'state', 'value']
    fieldvalues = (makeLink, makeGrid, makeNode, 'category', modifier.makeTime, modifier.makeTime, modifier.makeTime, 'state', 'value')

    tableid = modifier.addTableForModel('system', 'alert', fieldids, fieldnames, fieldvalues)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page
    return params

def match(j, args, params, tags, tasklet):
    return True
