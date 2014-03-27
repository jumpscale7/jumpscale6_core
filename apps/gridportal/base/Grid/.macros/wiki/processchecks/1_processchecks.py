import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc

    status = None
    out = list()

    out.append('||Node ID||Process Manager Status||Details||')
    status, errors = j.core.grid.healthchecker.checkProcessManagerAllNodes()

    for data in [status, errors]:
        if len(data) > 0:
            for nid, status in data.iteritems():
                status = status['processmanager']
                link = '[Details|nodestatus?nid=%s]' % nid if status[nid] else ''
                out.append('|[%s|node?id=%s]|%s|%s|' % (nid, nid, 'RUNNING' if status else 'HALTED', link))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
