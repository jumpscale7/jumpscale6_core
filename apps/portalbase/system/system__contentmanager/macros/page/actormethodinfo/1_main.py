
def main(o, args, params, tags, tasklet):
    page = args.page

    if "actorname" in args.paramsExtra:
        actorname = args.paramsExtra["actorname"]
    else:
        actorname = ""

    if "appname" in args.paramsExtra:
        appname = args.paramsExtra["appname"]
    else:
        appname = ""

    if "method" in args.paramsExtra:
        method = args.paramsExtra["method"]
    else:
        method = ""

    page2 = j.core.portal.runningPortal.webserver.getServiceInfo(appname=appname, actorname=actorname, methodname=method)

    page.addBootstrap()
    page.addMessage(page2.body)

    params.result = page
    return params


def match(o, args, params, tags, tasklet):
    return True
