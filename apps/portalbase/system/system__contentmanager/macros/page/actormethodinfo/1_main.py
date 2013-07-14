
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

    if args.paramsExtra.has_key("method"):
        method=args.paramsExtra["method"]
    else:
        method=""

    page2= o.core.portal.runningPortal.webserver.getServiceInfo(appname=appname,actorname=actorname,methodname=method)

    page.addBootstrap()
    page.addMessage(page2.body)

    params.result = page
    return params


def match(o,args,params,tags,tasklet):
    return True

