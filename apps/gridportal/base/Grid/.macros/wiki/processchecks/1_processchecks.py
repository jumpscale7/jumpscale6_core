import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc

    status = None
    out = list()

    out.append('||Node ID||Node Name||Process Manager Status||Details||')
    data, errors = j.core.grid.healthchecker.runAll()

    if len(data) > 0:
        for nid, checks in data.iteritems():
            if nid in errors:
                categories = errors[nid].keys()
                runningstring = '{color:orange}*RUNNING** (issues in %s){color}' % ', '.join(categories)
            else:
                runningstring = '{color:green}*RUNNING*{color}'
            status = checks['processmanager']
            link = '[Details|nodestatus?nid=%s]' % nid if status[nid] else ''
            out.append('|[%s|node?id=%s]|%s|%s|%s|' % (nid, nid, j.core.grid.healthchecker._nodenames[nid], runningstring if status[nid] else 'HALTED', link))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
