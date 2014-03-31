import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')

    out = list()

    out.append('||Port||Status||Memory Used||')
    
    rstatus, errors = j.core.grid.healthchecker.checkRedis(nid)
    for data in [rstatus, errors]:
        if len(data) > 0:
            rstatus = rstatus[nid]['redis']
            for port, stat in rstatus.iteritems():
                out.append('|%s|%s|%s|' % (port, '{color:green}*RUNNING*{color}' if stat['alive'] else '{color:red}HALTED{color}', stat['memory_usage']))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True


