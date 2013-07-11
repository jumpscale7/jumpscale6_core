def main(q,args,params,tags,tasklet):
    params.merge(args)
        
    doc=params.doc
    tags=params.tags
       
    doc=q.apps.system.contentmanager.extensions.defmanager.processDefs(doc)

    params.result=("",doc)
    
    return params


def match(q,args,params,tags,tasklet):
    return True
