import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc

    esdata = None
    out = list()

    esdata, errors = j.core.grid.healthchecker.checkElasticSearch()

    for message, data in {'OK': esdata, 'Not OK': errors}.iteritems():
        if len(data) > 0:
            data = data.values()[0]['elasticsearch']
            out.append('|*STATUS*|%s|' % message)
            for field in ['size', 'memory_usage']:
                out.append('|%s|%s|' % (field.title(), data[field]))
            for k, v in data['health'].iteritems():
                k = k.replace('_', ' ')
                out.append('|%s|%s|' % (k.title(), v))

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
