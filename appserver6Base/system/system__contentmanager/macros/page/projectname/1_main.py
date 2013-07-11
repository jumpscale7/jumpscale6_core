
def main(q,args,params,tags,tasklet):
    args.page.addBootstrap()
    args.page.projectname = args.cmdstr

    params.result = args.page
    return params


def match(q,args,params,tags,tasklet):
    return True

