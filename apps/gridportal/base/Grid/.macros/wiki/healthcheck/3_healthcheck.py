import JumpScale.grid.gridhealthchecker
import datetime
import time

def main(j, args, params, tags, tasklet):
    doc = args.doc
    
    out = list()
    results, errors = j.core.grid.healthchecker.checkStatusAllNodes()
    if errors:
        nodeids = errors.keys()
        out.append('h5. {color:red}Something on node(s) %s is not running.{color}' % ', '.join(["'%s'" % j.core.grid.healthchecker._nodenames[nodeid] for nodeid in nodeids]))
        out.append('For more details, check [here|/grid/checkstatus]')
    else:
        out.append('h5. {color:green}Everything seems to be OK{color}')

    results.update(errors)

    lastchecked = j.base.time.getEpochFuture('+3d')
    for nid, result in results.iteritems():
        for category, stats in result.iteritems():
            times = [float(x[1]) if x else lastchecked for x in stats.values()]
            times.append(lastchecked)
            times.sort()
            lastchecked = times[0]
    if lastchecked < time.time():
        lastchecked = datetime.datetime.fromtimestamp(lastchecked).strftime('%Y-%m-%d %H:%M:%S')
    else:
        lastchecked = 'N/A'
    out.append('The whole grid was last checked at: *%s*.' % lastchecked)

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
