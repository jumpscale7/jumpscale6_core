
def main(o,args,params,tags,tasklet):
    args.page.addBootstrap()
    args.page.projectname = args.cmdstr

    params.result = args.page
    return params


def match(o,args,params,tags,tasklet):
    return True

