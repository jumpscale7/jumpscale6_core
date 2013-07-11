
def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    params.result=""

    if params.paramsExtra.has_key("error"):
        #params.doc.content.replace(params.macrostr,)
        params.result=paramsExtra["error"]

    params.result=(params.result,params.doc)

    return params


def match(q,args,params,tags,tasklet):
    return True

