import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc

    status = None
    out = list()

    out.append('||Node ID||Process Manager Status||Details||')
    data, errors = j.core.grid.healthchecker.runAll()

    if len(data) > 0:
        for nid, checks in data.iteritems():
            runningstring = 'RUNNING'
            if nid in errors:
                categories = errors[nid].keys()
                runningstring += '*(issues in %s)' % ', '.join(categories)
            status = checks['processmanager']
            link = '[Details|nodestatus?nid=%s]' % nid if status[nid] else ''
            out.append('|[%s|node?id=%s]|%s|%s|' % (nid, nid, runningstring if status[nid] else 'HALTED', link))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
