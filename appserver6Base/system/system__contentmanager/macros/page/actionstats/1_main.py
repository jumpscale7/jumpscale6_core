
def main(q,args,params,tasklet):
    page = args.page


    nrhoursago=None
    state=None
    location=None
    channel=None

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

    p=params.requestContext.params
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


    params.result = page    
    return params


def match(q,args,params,tasklet):
    return True

