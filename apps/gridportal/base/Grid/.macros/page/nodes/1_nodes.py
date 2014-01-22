
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ['Id', 'Name', 'IP Address', 'Roles']
    def makeLink(row, field):
        return '[%s|/grid/node?id=%s]' % (row['id'], row['id'])

    fieldvalues = [makeLink, 'name', 'ipaddr', 'roles']
    fieldids = ['id', 'name', 'ipaddr', 'roles']
    modifier.addTableForModel('system', 'node', fieldids, fieldnames, fieldvalues)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
