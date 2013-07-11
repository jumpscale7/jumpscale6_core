
def main(q,args,params,tags,tasklet):
    page=args.page
    page.addMessage(args.cmdstr)
    params.result = page
    return params


def match(q,args,params,tags,tasklet):
    return True

