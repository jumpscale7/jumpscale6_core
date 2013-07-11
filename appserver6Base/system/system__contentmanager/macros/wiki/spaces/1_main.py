
def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    doc = params.doc

    out=""

    bullets=params.tags.labelExists("bullets")
    table=params.tags.labelExists("table")
    spaces = sorted(q.core.appserver6.runningAppserver.webserver.getSpaces())
    
    if table:
        for item in spaces:
            out+="|[%s|/%s]|\n" % (item,item.lower().strip("/"))
    
    else:

        for item in spaces:
            if item[0]<>"_" and item.strip()<>"":
                if bullets:
                    out+="* [%s|/%s]\n" % (item,item.lower().strip("/"))
                else:
                    out+="[%s|/%s]\n" % (item,item.lower().strip("/"))

    params.result=(out,doc)

    return params


def match(q,args,params,tags,tasklet):
    return True

