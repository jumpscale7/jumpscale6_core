
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ['Name', 'IP Address', 'Roles']
    def makeLink(row, field):
        return '[%s|/grid/node?id=%s]' % (row['name'], row['id'])

    fieldvalues = [makeLink, 'ipaddr', 'roles']
    fieldids = ['name', 'ipaddr', 'roles']
    tableid = modifier.addTableForModel('system', 'node', fieldids, fieldnames, fieldvalues)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
