
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)
    ecofilter = args.getTag('eco')
    filters = None
    if ecofilter:
        filters = {'eco':ecofilter}
    
    makeLink = '<a href=alert?guid=%(guid)s>%(id)s</a>' 
    makeGrid = '<a href=grid?id=%(gid)s>%(gid)s</a>'
    makeNode = '<a href=node?id=%(nid)s&gid=%(gid)s>%(nid)s</a>'

    fieldnames = ('Link to Alert', 'Grid ID', 'Node ID',  'Category', 'Raise Time','Last Time', 'Close Time', 'State', 'Assignee')
    fieldids = ['id', 'gid', 'nid',  'category', 'inittime', 'lasttime', 'closetime', 'state', 'assigned_user']
    fieldvalues = (makeLink, makeGrid, makeNode, 'category', modifier.makeTime, modifier.makeTime, modifier.makeTime, 'state', 'assigned_user')

    tableid = modifier.addTableForModel('system', 'alert', fieldids, fieldnames, fieldvalues, filters)

    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page
    return params

def match(j, args, params, tags, tasklet):
    return True
