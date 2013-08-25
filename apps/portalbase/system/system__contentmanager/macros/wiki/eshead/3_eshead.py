
def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc
    tags = params.tags.getDict()
    host = j.core.portal.runningPortal.dns
    out = "<iframe src='%s' width='%s' height='%s'></iframe>" % ('/eshead?base_uri=http://%s:9200' % host, '100%', '800px')

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
