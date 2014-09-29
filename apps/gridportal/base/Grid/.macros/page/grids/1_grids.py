
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ['GID', 'Name']

    namelink = '[%(name)s|/grid/nodes?gid=%(id)s]'
    fieldvalues = ['id', namelink]
    fieldids = ['id', 'name']
    tableid = modifier.addTableForModel('system', 'grid', fieldids, fieldnames, fieldvalues)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
