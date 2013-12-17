
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")
    
    idd=int(args.tags.getDict()["id"])

    obj=actor.getNodes(id=idd)
    
    doc.content=doc.applyParams(obj[0],content=doc.content)

    params.result = (doc, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
