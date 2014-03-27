import JumpScale.grid.gridhealthchecker
import datetime

def main(j, args, params, tags, tasklet):
    doc = args.doc
    
    out = list()
    checks, errors = j.core.grid.healthchecker.checkStatusAllNodes()
    for nid, check in checks.iteritems():
        check = check['healthcheck']
        if not check['health']:
            out.append('h4. Something on node %s is not running.' % nid)
            out.append("""{{cssstyle
                        h4 { color: red;}
                    }}""")

    if len(out) == 0:
        out.append("""{{cssstyle\n
                h4 { color: green;  }\n
                }}""")
        out.append('h4. Healthcheck: OK')

    # lastchecked = checks.get('time')
    # if lastchecked:
    #     lastchecked = datetime.datetime.fromtimestamp(float(lastchecked)).strftime('%Y-%m-%d %H:%M:%S')
    # else:
    #     lastchecked = 'N/A'
    # out.append('h5. last checked at: %s.' % lastchecked)

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
