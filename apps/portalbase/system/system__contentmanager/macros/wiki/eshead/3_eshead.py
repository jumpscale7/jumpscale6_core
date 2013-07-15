
def main(o,args,params,tags,tasklet):
    params.merge(args)
    
    doc = params.doc
    tags = params.tags.getDict()
    #import pdb; pdb.set_trace()
    out = "<iframe src='%s' width='%s' height='%s'></iframe>" % ('/eshead', '100%', '800px')

    params.result = (out, doc)

    return params


def match(o,args,params,tags,tasklet):
    return True

