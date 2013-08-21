def main(o,args,params,tags,tasklet):
    params.merge(args)
        
    doc=params.doc
    tags=params.tags
       
    defmanager=o.apps.system.contentmanager.extensions.defmanager

    defs=defmanager.getDefListWithLinks()

    out="{{code:\n"

    firstletter=""
    for name,link,aliases in defs:
        aliases.sort()
        if aliases<>[]:
            out +="* %s (%s)\n"%(name,",".join(aliases))
        else:
            out +="* %s\n"%name

    out+="}}\n"
    
    params.result=(out,doc)
    
    return params


def match(o,args,params,tags,tasklet):
    return True
