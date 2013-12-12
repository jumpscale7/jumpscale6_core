def main(j, args, params, tags, tasklet):

    page = args.page

    page.addHeading('Grid Information', 3)

    import JumpScale.grid.osis
    osiscl = j.core.osis.getClient()
    client = j.core.osis.getClientForCategory(osiscl, 'system', 'grid')

    grid = client.search('null')

    fields = ('id', 'useavahi', 'ipaddr', 'name', 'nid')

    rows = list()
    for k,v in sorted(grid['result'][0]['_source'].iteritems()):
        v = v or ""
        if k not in fields:
            continue
        if k == 'useavahi':
            v = 'used' if v == 1 else 'Not used'
        elif k in ('ipaddr'):
            rows.append(["<th>%s</th>" %k,"", ""])
            for kc in v:
                rows.append(["<th></th>", "",kc])
        else:
            rows.append(["<th>%s</th>" %k,"", v])

    page.addList(rows)
    page.addHTML('<br><br><br><br><br>')

    page.addHeading('Grid Nodes', 3)

    modifier = j.html.getPageModifierGridDataTables(page)
    url = '/restmachine/system/logs/listNodes?'

    fieldnames = ('name', 'roles', 'ipaddr', 'machineguid', 'guid', 'GoTo')
    page = modifier.addTableFromURL(url, fieldnames)
    # if 'result' in nodes:

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
