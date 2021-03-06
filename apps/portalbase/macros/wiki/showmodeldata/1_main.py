
def main(j, args, params, tags, tasklet):
    params.merge(args)

    params.result = ""

    tags = params["tags"]

    id = tags.tagGet("id")
    model = tags.tagGet("model")
    actor = tags.tagGet("actor")
    application = tags.tagGet("application")
    if application == "":
        application = "system"

    # if application=="":
    #     result="application is not specified in macro"
    #     params.result=(result,params.doc)
    #     return params

    if model == "":
        result = "model is not specified in macro"
        params.result = (result, params.doc)
        return params

    if actor == "":
        result = "actor is not specified in macro"
        params.result = (result, params.doc)
        return params

    if id.find("$$") != -1:
        result = "please call this page with some id e.g. otherwise the model %s from actor %s cannot be found, example: ?id=121 " % (model, actor)
        params.result = (result, params.doc)
        return params

    actor2 = j.core.portal.active.actorsloader.getActor(application, actor)

    try:
        model = actor2.models.__dict__[model].get(id=id)
    except:
        result = "could not find model %s from actor %s with id %s." % (model, actor, id)
        params.result = (result, params.doc)
        return params

    hrd = j.core.hrd.getHRDFromOsisObject(model, True)

    result = "{{code:\n%s\n}}" % hrd

    params.result = (result, params.doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
