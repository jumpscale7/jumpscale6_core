import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')

    out = list()

    out.append('||Disk||Status||')
    
    disks, errors = j.core.grid.healthchecker.checkDisks(nid)

    for message, data in {'OK': disks, 'Not Okay': errors}.iteritems():
        if len(data) < 0:
            out.append('|*STATUS*|%s|' % message)
            data = data[nid]['disks']
            for disk, msg in data.iteritems():
                out.append('|%s|%s|' % (disk, msg))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True


