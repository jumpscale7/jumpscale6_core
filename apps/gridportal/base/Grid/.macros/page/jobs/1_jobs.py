
def main(j, args, params, tags, tasklet):

    page = args.page
    nid = args.getTag("nid")
    if not nid and args.tags.tagExists('nid'):
        page.addMessage('Missing node id param "id"')
        params.result = page
        return params

    filters = dict()
    for tag, val in args.tags.getDict().iteritems():
        val = args.getTag(tag)
        if tag == 'from' and val:
            filters[tag] = j.base.time.getEpochAgo(val)
        elif val:
            filters[tag] = val

    modifier = j.html.getPageModifierGridDataTables(page)

    def makeLink(row, field):
        return '[%s|/grid/job?id=%s]' % (row['id'], row['id'])

    fieldnames = ['Id', 'Category', 'Result', 'JSName', 'JSOrganization', 'State', 'Description']
    fieldvalues = [makeLink, 'category', 'result', 'jsname', 'jsorganization', 'state', 'description']
    fieldids = ['id', 'category', 'result', 'jsname', 'jsorganization', 'state', 'description']
    tableid = modifier.addTableForModel('system', 'job', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
