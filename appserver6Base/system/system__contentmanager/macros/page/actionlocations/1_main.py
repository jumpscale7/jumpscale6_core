
def main(q,args,params,tags,tasklet):

    page = params.page

    al=q.apps.acloudops.actionlogger
    lh = al.extensions.loghandler

    lh.init()
        
    page.addCodeBlock(str(lh.actionssource))
    
    #lh.actiontypes

    params.result = page
    return params


def match(q,args,params,tags,tasklet):

    return True

