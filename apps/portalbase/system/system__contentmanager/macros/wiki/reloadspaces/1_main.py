
def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    out=""
    spaces=q.core.appserver6.runningAppserver.webserver.spacesloader.spaces
    for spacename in spaces:
        out+="* [%s|/system/ReloadSpace/?name=%s]\n" % (spacename,spacename)

    params.result=(out,params.doc)

    return params


def match(q,args,params,tags,tasklet):
    return True

