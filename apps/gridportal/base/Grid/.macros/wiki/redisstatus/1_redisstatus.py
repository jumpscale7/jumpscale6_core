import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')

    out = list()

    out.append('||Port||Status||Memory Used||')
    
    rstatus = j.core.grid.healthchecker.checkRedis(nid)
    for port, stat in rstatus.iteritems():
        out.append('|%s|%s|%s|' % (port, stat['alive'], stat['memory_usage']))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True


