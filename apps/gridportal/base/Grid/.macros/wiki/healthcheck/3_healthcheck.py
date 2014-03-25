import JumpScale.grid.gridhealthchecker
import datetime

def main(j, args, params, tags, tasklet):
    doc = args.doc
    
    out = list()
    for node in j.apps.system.gridmanager.getNodes():
        nid = node['id']
        checks = j.core.grid.healthchecker.gatherNodeChecks(nid)['result']
        for check, status in checks.iteritems():
            if check == 'time':
                continue
            if not status:
                out.append('h3. %s is not Running' % check)

    if len(out) == 0:
        out.append("""{{cssstyle\n
                h3 { color: green;  }\n
                }}""")
        lastchecked = checks.get('time')
        if lastchecked:
            lastchecked = datetime.datetime.fromtimestamp(float(lastchecked)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            lastchecked = 'N/A'
        out.append('h3. Healthcheck: OK')
        out.append('h5. last checked at: %s.' % lastchecked)
    else:
        out.append("""{{cssstyle
                    h3 { color: red;  }
                }}""")
    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
