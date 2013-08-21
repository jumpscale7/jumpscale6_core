import copy
def main(o,args,params,tags,tasklet):
    page = args.page


    actor=""
    actionname=""
    detail="" #1 or 0 (if detail will get detailed stats)

    if args.tags.tagExists("detail"):
        detail=int(args.tags.tagGet("detail"))

    if args.tags.tagExists("actor"):
        actor=str(args.tags.tagGet("actor")).lower().strip()

    if args.tags.tagExists("actionname"):
        actionname=str(args.tags.tagGet("actionname")).lower().strip()

    p=args.requestContext.params
    if p.has_key("detail"):
        detail=int(p["detail"])
    if p.has_key("actor"):
        actor=p["actor"].lower().strip()
    if p.has_key("actionname"):
        actionname=p["actionname"].lower().strip()

    if len(actionname)>0 and actionname[0]=="_":
        actionname=actionname[1:]

    al=o.apps.acloudops.actionlogger
    lh=al.extensions.loghandler

    lh.init()
    
        
    for key in lh.actiontypes.keys():
        at=lh.actiontypes[key]

        found=True
        actor2,actionname2=key.split("_",1)
        if actionname2<>"" and actionname2[0]=="_":
            actionname2=actionname2[1:]
        
        if actor<>"" and actor<>actor2:
            found=False

        if actionname<>"" and actionname<>actionname2:
            found=False
            
        if found:
            at2=copy.copy(at)
            if detail<>1:
                at2.stats={}
            page.addHeading(key,4)
            page.addCodeBlock(str(at2))
        
        

    params.result = page
    return params


def match(o,args,params,tags,tasklet):
    return True

