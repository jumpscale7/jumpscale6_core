import JumpScale.grid.gridhealthchecker

def main(j, args, params, tags, tasklet):
    doc = args.doc

    esdata = None
    out = list()

    esdata = j.core.grid.healthchecker.checkElasticSearch()
    if esdata == None:
        esdata = 'N/A'
    if esdata['size']:
        size = esdata['size']/1024
        esnotes = '%sKB' % size
    for k, v in esdata['health'].iteritems():
        k = k.replace('_', '')
        out.append('|%s|%s|' % (k, v))
    out.append('|Size|%s|' % esnotes)

    out = '\n'.join(out)

    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
