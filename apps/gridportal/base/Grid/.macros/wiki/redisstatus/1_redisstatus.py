import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc
    nid = args.getTag('nid')

    out = list()

    out.append('||Port||Status||Memory Used||')

    rstatus, errors = j.core.grid.healthchecker.checkRedis(nid)
    for data in [rstatus, errors]:
        if len(data) > 0:
            rstatus = data[nid]['redis']
            for port, stat in rstatus.iteritems():
                if stat['alive'] is True:
                    state = '{color:green}*RUNNING*{color}'
                elif stat['alive'] is False:
                    state = '{color:red}HALTED*{color}'
                else:
                    state = '{color:orange}UNKOWN{color}'
                out.append('|%s|%s|%s|' % (port, state, stat['memory_usage']))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True


