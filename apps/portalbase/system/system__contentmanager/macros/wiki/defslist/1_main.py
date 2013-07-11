def main(q,args,params,tags,tasklet):
    params.merge(args)
        
    doc=params.doc
    tags=params.tags
       
    defmanager=q.apps.system.contentmanager.extensions.defmanager

    defs=defmanager.getDefListWithLinks()

    out=""

    firstletter=""
    for name,link,aliases in defs:
        if name[0]<>firstletter:
            out += "h3. %s\n" % name[0].upper()
            firstletter=name[0]
        out +="* %s\n"%link
    
    params.result=(out,doc)
    
    return params


def match(q,args,params,tags,tasklet):
    return True
