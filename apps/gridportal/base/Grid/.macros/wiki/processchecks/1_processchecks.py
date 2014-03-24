import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc

    status = None
    out = list()

    out.append('||Node||Process Manager Status||Details||')
    for node in j.apps.system.gridmanager.getNodes():
        nid = node['id']
        status = j.core.grid.healthchecker.checkProcessManagers(nid)
        if status == None:
            status = 'N/A'
        out.append('|[*%s*|node?id=%s]|%s|[Details|nodestatus?nid=%s]|' % (node['name'], nid, status, nid))

    out = '\n'.join(out)
    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
