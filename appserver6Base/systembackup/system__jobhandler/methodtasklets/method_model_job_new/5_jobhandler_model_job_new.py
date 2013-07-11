
def main(q,args,params,tags,tasklet):
    #new
    appname="system"
    actorname="jobhandler"
    modelname="job"
    modeldb=q.apps.system.jobhandler.models.job
    obj=modeldb.new()
    modeldb.set(obj)
    params.result={}
    params.result["pymodelobject"]=obj.obj2dict()
    params.result["pymodeltype"]="system__jobhandler__job"
    return params

def match(q,args,params,tags,tasklet):
    return True
