
def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    name=params.tags.tagGet("name")

    out="space %s succesfully reloaded." % name

    if name.find("$$")<>-1:
        out="ERROR: could not reload the docs for space because param was not specified (need to have param name)."
        params.result=out

        return params

    
    try:
        space=q.core.appserver6.runningAppserver.webserver.loadSpace(name)
        
    except Exception,e:
        error=e
        out="ERROR: could not reload the docs for space %s, please check event log." % params.tags.tagGet("name")
        eco=q.errorconditionhandler.parsePythonErrorObject(e)
        q.errorconditionhandler.processErrorConditionObject(eco)
        print eco



    params.result=(out,params.doc)

    return params


def match(q,args,params,tags,tasklet):
    return True

