
def main(o,args,params,tags,tasklet):
    params.merge(args)
    
    params.result=""

    tags=params["tags"]

    id=tags.tagGet("id")
    model=tags.tagGet("model")
    actor=tags.tagGet("actor")
    application=tags.tagGet("application")
    if application=="":
        application="system"

    # if application=="":
    #     result="application is not specified in macro"
    #     params.result=(result,params.doc)
    #     return params

    if model=="":
        result="model is not specified in macro"
        params.result=(result,params.doc)
        return params

    if actor=="":
        result="actor is not specified in macro"
        params.result=(result,params.doc)
        return params

    if id.find("$$")<>-1:
        result="please call this page with some id e.g. otherwise the model %s from actor %s cannot be found, example: ?id=121 " % (model,actor)
        params.result=(result,params.doc)
        return params


    actor=o.core.portal.runningPortal.actorsloader.getActor(application,actor)

    actor.models.machine.exists(id=id)
    try:
        model=actor.models.__dict__[model].get(id=id)
    except Exception,e:
        from IPython import embed
        print "DEBUG NOW ooo"
        embed()
        
        result="could not find model %s from actor %s with id %s." % (model,actor,id)
        params.result=(result,params.doc)
        return params


    # o.core.portal.runningPortal.activateActor(

    from IPython import embed
    print "DEBUG NOW getdata"
    embed()
    

    params.result=(result,params.doc)

    return params.result


def match(o,args,params,tags,tasklet):
    return True

