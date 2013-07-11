
def main(q,args,params,tags,tasklet):
    page = args.page
    page.addBootstrap()    
    page.hasfindmenu=True
    page._hasmenu=True
    params.result = page
    return params

def match(q,args,params,tags,tasklet):
    return True

