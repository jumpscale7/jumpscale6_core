import copy
def main(o,args,params,tags,tasklet):
    params.merge(args)    
    page=params.page
    tags=params.tags

    al=o.apps.acloudops.actionlogger
    lh=al.extensions.loghandler

    lh.init()
    
    header=["actor","actionname","link"]
    row=[]
    
    keys=copy.copy(lh.actiontypes.keys())
    keys.sort()
    for key in keys:
        at=lh.actiontypes[key]

        found=True
        actor2,actionname2=key.split("_",1)
        if actionname2<>"" and actionname2[0]=="_":
            actionname2=actionname2[1:]
        row.append([actor2,actionname2,"link__/CloudHealth/ActionTypes?detail=1&actor=%s&actionname=%s" % (actor2,actionname2)])
                
        

    page.addList(row,header,linkcolumns=[2])
    return params


def match(o,args,params,tags,tasklet):
    return True

