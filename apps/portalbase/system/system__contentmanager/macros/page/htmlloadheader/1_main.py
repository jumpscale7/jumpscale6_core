
def main(o,args,params,tags,tasklet):

    page = args.page
    
    if len(args.doc.htmlHeadersCustom)<1:
        raise RuntimeError("Could not find custom html header on doc %s"%args.doc.name)

    page.addHTMLHeader(args.doc.htmlHeadersCustom[0])

    params.result = page
    return params


def match(o,args,params,tags,tasklet):
    return True

