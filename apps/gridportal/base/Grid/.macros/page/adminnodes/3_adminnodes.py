
def main(j, args, params, tags, tasklet):


    from IPython import embed
    print "DEBUG NOW kkkk"
    embed()
    
    #@todo implement below

    try:
        import JumpScale.baselib.watchdog.manager
    except:
        page = args.page
        page.addMessage('* Alerts are not configured')
        params.result = page
        return params

    def _formatdata():
        aaData = list()

        for gguid in j.tools.watchdog.manager.getGGUIDS():
            for alert in j.tools.watchdog.manager.iterateAlerts(gguid=gguid):
                itemdata = list()
                epochHR = j.base.time.epoch2HRDateTime(alert.epoch)
                epochEsc = j.base.time.epoch2HRDateTime(alert.escalationepoch)
                link = '<a href=alert?gguid=%s&key=%s_%s>Details</a>' % (alert.gguid, alert.nid, alert.category)
                node = '<a href=node?id=%s>%s</a>' % (alert.nid, alert.nid)
                grid = '<a href=grid?id=%s>%s</a>' % (alert.gid, alert.gid)
                for field in [link, grid, node, alert.category, epochHR, epochEsc, alert.state, alert.value]:
                    itemdata.append(str(field))
                aaData.append(itemdata)
        aaData = str(aaData)
        return aaData.replace('[[', '[ [').replace(']]', '] ]')

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ('Link to Alert', 'Grid ID', 'Node ID', 'Category', 'Raise Time','Escalation Time', 'State', 'Value')
    tableid = modifier.addTableFromData(_formatdata(), fieldnames)

    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
