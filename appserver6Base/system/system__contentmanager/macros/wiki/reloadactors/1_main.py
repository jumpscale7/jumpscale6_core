
def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    out=""
    from pylabs.Shell import ipshellDebug,ipshell
    print "DEBUG NOW reload actors macro"
    ipshell()
    
    spaces=q.core.appserver6.runningAppserver.webserver.spacesloader.spaces    
    for spacename in spaces.keys():
        model=spaces[spacename].model  
        out+="* [%s|/system/ReloadApplication/?name=%s]\n" % (item,item.lower().strip("/"))

    params.result=(out,params.doc)

    return params


def match(q,args,params,tags,tasklet):
    return True

