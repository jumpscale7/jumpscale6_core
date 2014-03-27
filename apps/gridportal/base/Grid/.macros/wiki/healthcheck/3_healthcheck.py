import JumpScale.grid.gridhealthchecker
import datetime

def main(j, args, params, tags, tasklet):
    doc = args.doc
    
    out = list()
    resutls, errors = j.core.grid.healthchecker.runAll()
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
