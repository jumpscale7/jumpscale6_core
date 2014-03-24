import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')

    out = list()

    out.append('||Disk||Status||')
    
    workers = j.core.grid.healthchecker.checkDisks(nid)
    for disk, msg in workers.iteritems():
        out.append('|%s|%s|' % (disk, msg))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True


