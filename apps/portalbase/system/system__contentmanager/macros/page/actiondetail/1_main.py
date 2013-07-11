
def main(q,args,params,tags,tasklet):

    page = args.page


    actionJobGuid=None

    if args.tags.tagExists("id"):
        actionJobGuid = args.tags.tagGet("id")

    p = args.requestContext.params
    if p.has_key("jobguid"):
        actionJobGuid=p["jobguid"]

    al=q.apps.acloudops.actionlogger
    lh=al.extensions.loghandler

    lh.init()
    
    if lh.actions.has_key(actionJobGuid):
        action=lh.actions[actionJobGuid]
    else:
        page.addMessage("Could not find action with jobguid:%s" % actionJobGuid)

    a=lh.getActionFullInfo(action)

    page.addHeading("%s %s %s" % (action.customername,a["actiontype"].action,a["actiontype"].actor),3)                
    
    page.addDescr("channel",a["source"].channel)
    page.addDescr("location",a["source"].location)
    page.addDescr("customername",action.customername)
    page.addDescr("spacename",action.spacename)     
    page.addDescr("resourcename",action.resourcename)
    page.addDescr("resourceguid",action.resourceguid)
    page.addDescr("state",action.state)
    page.addDescr("start",q.base.time.epoch2HRDateTime(action.start))
    page.addDescr("hour",action.hour)

    page.addHeading("action type history info",3)
    page.addCodeBlock(str(a["actiontype"]))

    params.result = page
    return params


def match(q,args,params,tags,tasklet):
    return True

