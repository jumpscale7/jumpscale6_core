
def main(j, args, params, tags, tasklet):
    import ujson

    page = args.page
    nid = args.getTag("nid")
    if not nid and args.tags.tagExists('nid'):
        page.addMessage('Missing node id param "id"')
        params.result = page
        return params

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        if tag == 'from' and val:
            filters['from_'] = {'name': 'timeStart', 'value': j.base.time.getEpochAgo(val), 'eq': 'gte'}
        elif tag == 'to' and val:
            filters['to'] = {'name': 'timeStop', 'value': j.base.time.getEpochAgo(val), 'eq': 'lte'}
        elif val:
            filters[tag] = val

    modifier = j.html.getPageModifierGridDataTables(page)
    linkstr = '[%(id)s|/grid/job?id=%(id)s]'

    def makeResult(row, field):
        result = row[field]
        try:
            result = ujson.loads(result)
        except:
            pass
        return result

    fieldnames = ['Id', 'Category', 'Command', 'Result', 'State']
    fieldvalues = [linkstr, 'category', 'cmd', makeResult, 'state']
    fieldids = ['id', 'category', 'cmd', 'result', 'state']
    tableid = modifier.addTableForModel('system', 'job', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
