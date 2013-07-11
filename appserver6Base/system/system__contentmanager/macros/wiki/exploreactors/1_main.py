import os

def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    out=""

    actors=q.core.appserver6.runningAppserver.actorsloader.actors

    for ttype in ["specs","methodtasklets","extensions","wikimacros"]:

        out+="h3. Actor %s\n" %ttype.capitalize()

        for actorname in actors.keys():
            model=actors[actorname].model   #@todo security breach
            path=os.path.abspath(model.path)
            q.system.fs.createDir(path) 
            path=path.replace(":","___").replace("/","\\")+"\\%s\\"%ttype
            # out+="|[%s | /system/Explorer/?path=%s] |[reload | /system/reloadactor/?name=%s]|\n" % (model.id,path,model.id)
            out+="|[%s | /system/Explorer/?path=%s] |\n" % (model.id,path)

    params.result=out

    params.result=(params.result,params.doc)

    return params

def match(q,args,params,tags,tasklet):
    return True

