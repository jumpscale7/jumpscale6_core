import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')

    out = list()

    disks, errors = j.core.grid.healthchecker.checkDisks(nid)

    out.append('||Disk||Free Space||Status||')
    for data in [disks, errors]:
        if len(data) > 0:
            data = data[nid]['disks']
            for path, diskstat in data.iteritems():
                out.append('|%s|%s|%s|' % (path, diskstat['message'], 'OK' if diskstat['status'] else 'Not OK'))
            out.append('\n')

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True


