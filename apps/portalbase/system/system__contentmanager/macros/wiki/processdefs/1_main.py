def main(o,args,params,tags,tasklet):
    params.merge(args)
        
    doc=params.doc
    tags=params.tags
       
    doc=o.apps.system.contentmanager.extensions.defmanager.processDefs(doc)

    params.result=("",doc)
    
    return params


def match(o,args,params,tags,tasklet):
    return True
