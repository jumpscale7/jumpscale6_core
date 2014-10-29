try:
    import ujson as json
except:
    import json


def main(j, args, params, tags, tasklet):
    params.merge(args)
    doc = params.doc
    data = args.getTag('data')
    title = args.getTag('title')

    out = "*%s*\n" % title
    try:    
        objargs = json.loads(data)
        for key,value in objargs.iteritems():
            if not value:
                value = ''
            out += "|%s|%s|\n"%(str(key),j.html.escape(str(value)))
    except Exception:
        out = ''
    params.result = (out, doc)
    return params
    

def match(j, args, params, tags, tasklet):
    return True
