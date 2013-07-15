import copy
def main(o,args,params,tasklet):

    page = args.page

    nrhoursago=None
    state=None
    location=None
    channel=None
    actor=""
    actionname=""

    if args.tags.tagExists("nrhoursago"):
        nrhoursago=int(args.tags.tagGet("nrhoursago"))

    if args.tags.tagExists("state"):
        state=str(args.tags.tagGet("state")).lower().strip()

    if args.tags.tagExists("location"):
        location=str(args.tags.tagGet("location")).lower().strip()

    if args.tags.tagExists("channel"):
        channel=str(args.tags.tagGet("channel")).lower().strip()

    if args.tags.tagExists("actor"):
        actor=str(args.tags.tagGet("actor")).lower().strip()

    if args.tags.tagExists("actionname"):
        actionname=str(args.tags.tagGet("actionname")).lower().strip()

    p = args.requestContext.params
    if p.has_key("nrhoursago"):
        nrhoursago=int(p["nrhoursago"])
    if p.has_key("state"):
        state=p["state"].lower().strip()
    if p.has_key("location"):
        location=p["location"].lower().strip()
    if p.has_key("channel"):
        channel=p["channel"].lower().strip()
    if p.has_key("actor"):
        actor=p["actor"].lower().strip()
    if p.has_key("actionname"):
        actionname=p["actionname"].lower().strip()


    al=o.apps.acloudops.actionlogger
    lh=al.extensions.loghandler

    actions=al.getActions(nrhoursago, state, location, channel,actor,actionname)
    
    if len(actions)>500:
        page.addMessage("too many results in query please specify other query, nr results were %s."%len(actions))
    
    locations={}
    
    for action in actions:
        if not locations.has_key(action.source):
            locations[action.source]={}
        day=q.base.time.epoch2HRDate(action.start)
        daykey=str(action.source)+"_"+str(day)
        if not locations[action.source].has_key(daykey):
            locations[action.source][daykey]=[]        
        locations[action.source][daykey].append(action.jobguid)
        
    for locid in locations.keys():
        loc=lh.actionssource[lh.actionssourceId2Key[locid]]
        page.addHeading("%s %s" % (loc.channel,loc.location),2)
        keys=copy.copy(locations[locid].keys())
        keys.sort()
        for dayid in keys:
            day=dayid.split("_")[1]
            page.addHeading("day %s" % (day),4)    
            rows=[]
            header=["actor","action","start","duration","state","customername","link"]
            
            for actionid in locations[locid][dayid]:
                action=lh.actions[actionid]
                actor,actionm=lh.actiontypesId2Key[action.actiontype].split("_",1)
                    
                start=q.base.time.epoch2HRTime(action.start)
                duration=action.stop-action.start
                rows.append([actor,actionm,start,duration,action.state,action.customername,"details__/CloudHealth/ActionDetail/?jobguid=%s"%action.jobguid])            
                
            page.addList(rows,header,linkcolumns=[6])
        
    params.result = page 
    return params


def match(o,args,params,tasklet):
    return True

