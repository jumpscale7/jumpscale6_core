import json


def main(j, args, params, tags, tasklet):
    params.merge(args)
    doc = params.doc
    data = args.getTag('data')
    title = args.getTag('title')

    out = "*%s*\n" % title
    if data:
        objargs = json.loads(data)
        for key,value in objargs.iteritems():
            out += "|%s|%s|\n"%(str(key),j.html.escape(str(value)))
    else:
        out = ''
    params.result = (out, doc)
    return params
    

def match(j, args, params, tags, tasklet):
    return True
