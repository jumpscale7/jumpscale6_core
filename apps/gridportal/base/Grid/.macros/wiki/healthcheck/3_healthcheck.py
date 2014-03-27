import JumpScale.grid.gridhealthchecker
import datetime
import time

def main(j, args, params, tags, tasklet):
    doc = args.doc
    
    out = list()
    results, errors = j.core.grid.healthchecker.checkStatusAllNodes()
    if errors:
        nodes = errors.keys()
        out.append('h4. Something on node(s) %s is not running.' % ', '.join([str(x) for x in nodes]))
        out.append('For more details, check [here|/grid/checkstatus]')
        out.append("""{{cssstyle
                    h4 { color: red;}
                }}""")
    else:
        out.append("""{{cssstyle\n
                h4 { color: green;  }\n
                }}""")
        out.append('h4. Everything seems to be OK')

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
    out.append('h5. last checked at: %s.' % lastchecked)

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
