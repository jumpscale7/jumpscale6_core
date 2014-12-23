
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ['GID', 'Name', 'Node ID', 'IP Address', 'Roles']
    filters = dict()
    nativequery = None
    for tag, val in args.tags.tags.iteritems():
        if tag in ('gid', ) and val and not val.startswith("$$"):
            filters['gid'] = int(val)
    if args.getTag('roles'):
        filters['roles'] = args.getTag('roles')

    namelink = '[%(name)s|/grid/node?id=%(id)s&gid=%(gid)s]'
    fieldvalues = ['gid', namelink, 'id','ipaddr', 'roles']
    fieldids = ['gid', 'name', 'id', 'ipaddr', 'roles']
    tableid = modifier.addTableForModel('system', 'node', fieldids, fieldnames, fieldvalues, filters, nativequery)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
