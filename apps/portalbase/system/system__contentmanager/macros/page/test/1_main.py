
def main(o,args,params,tags,tasklet):
        
    page = args.page
    page.addMessage(str(params.requestContext.params))
    params.result = page 
    return params


def match(o,args,params,tags,tasklet):
    return True

