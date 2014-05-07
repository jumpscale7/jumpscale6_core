import JumpScale.baselib.watchdog.manager
import json

def main(j, args, params, tags, tasklet):
    def _formatdata():
        aaData = list()

        for gguid in j.tools.watchdog.manager.getGGUIDS():
            for alert in j.tools.watchdog.manager.iterateAlerts(gguid=gguid):
                itemdata = list()
                epochHR = j.base.time.epoch2HRDateTime(alert.epoch)
                epochEsc = j.base.time.epoch2HRDateTime(alert.escalationepoch)
                for field in [alert.gid, alert.nid, alert.category, epochHR, epochEsc, alert.state, alert.value]:
                    itemdata.append(str(field))
                aaData.append(itemdata)
        aaData = str(aaData)
        return aaData.replace('[[', '[ [').replace(']]', '] ]')

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ('Grid ID', 'Node ID', 'Category', 'Raise Time','Escalation Time', 'State', 'Value')
    tableid = modifier.addTableFromData(_formatdata(), fieldnames)

    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
