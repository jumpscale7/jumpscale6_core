import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc

    esdata = None
    out = list()

    esdata, errors = j.core.grid.healthchecker.checkElasticSearch()

    for message, data in {'OK': esdata, 'HALTED': errors}.iteritems():
        if len(data) > 0:
            data = data.values()[0]['elasticsearch']
            out.append('|Status|{color:green}*%s*{color}|' % message)
            out.append('|%s|%s|' % ('Size', data['size']))
            out.append('|%s|%s|' % ('Memory Usage', data['memory_usage']))

            for k, v in data['health'].iteritems():
                if k == 'status':
                    out.append('|%s|{color:%s}*%s*{color}|' % (k.title(), v, v.upper()))
                    continue
                k = k.replace('_', ' ')
                out.append('|%s|%s|' % (k.title(), v))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
