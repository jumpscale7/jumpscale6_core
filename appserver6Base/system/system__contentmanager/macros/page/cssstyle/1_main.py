
def main(q,args,params,tags,tasklet):
    page = args.page
    cmdstr = args.cmdstr
    page.addCSS(cssContent=cmdstr)

    params.result = page
    
    return params


def match(q,args,params,tags,tasklet):
    return True

