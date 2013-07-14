
def main(o,args,params,tags,tasklet):
    page = args.page


    if args.paramsExtra.has_key("actorname"):
        actorname=args.paramsExtra["actorname"]
    else:
        actorname=""

    if args.paramsExtra.has_key("appname"):
        appname=args.paramsExtra["appname"]
    else:
        appname=""

    page2= o.core.portal.runningPortal.webserver.getServicesInfo(appname=appname,actor=actorname)

    page.addBootstrap()
    page.addMessage(page2.body)

    params.result = page
    return params


def match(q,args,params,tags,tasklet):
    return True

