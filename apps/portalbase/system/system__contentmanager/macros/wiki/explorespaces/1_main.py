import os

def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    out=""

    spaces = q.core.appserver6.runningAppserver.webserver.spacesloader.spaces

    for spacename in sorted(spaces.keys()):
        model=spaces[spacename].model   #@todo security breach

        path=os.path.abspath(model.path)
        path=path.replace(":","___").replace("/","\\")
        
        out+="| [%s | /system/Explorer/?path=%s] | [Reload | /system/ReloadSpace/?name=%s]|\n" % \
            (model.id,path,model.id)

    params.result=(out,params.doc)

    return params

def match(q,args,params,tags,tasklet):
    return True

