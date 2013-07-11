
def main(q,args,params,tags,tasklet):
    #delete
    appname="system"
    actorname="jobhandler"
    modelname="job"
    modeldb=q.apps.system.jobhandler.models.job
    try:
        obj=modeldb.get(params.id)
    except Exception,e:
        if str(e).find("Key value store doesnt have a value for key")<>-1:
            #did not find
            params.result=False
            return params

    params.result={}
    params.result["pymodelobject"]=obj.obj2dict()
    params.result["pymodeltype"]="system__jobhandler__job"
    return params

def match(q,args,params,tags,tasklet):
    return True
