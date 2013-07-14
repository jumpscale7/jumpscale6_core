
def main(o,args,params,tags,tasklet):
    params.merge(args)
    
    out=""
    spaces=o.core.portal.runningPortal.webserver.spacesloader.spaces
    for spacename in spaces:
        out+="* [%s|/system/ReloadSpace/?name=%s]\n" % (spacename,spacename)

    params.result=(out,params.doc)

    return params


def match(o,args,params,tags,tasklet):
    return True

