import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc

    status = None
    out = list()

    out.append('||Node||Node ID||Process Manager Status||Details||')
    for node in j.apps.system.gridmanager.getNodes():
        nid = node['id']
        status = j.core.grid.healthchecker.checkProcessManagers(nid)
        link = '[Details|nodestatus?nid=%s]' % nid if status else ''
        out.append('|[*%s*|node?id=%s]|%s|%s|%s|' % (node['name'], nid, nid, 'RUNNING' if status else 'HALTED', link))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
