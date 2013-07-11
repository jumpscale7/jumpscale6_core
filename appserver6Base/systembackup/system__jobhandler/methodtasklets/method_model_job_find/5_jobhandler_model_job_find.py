
def main(q,args,params,tags,tasklet):
    #find
    appname="system"
    actorname="jobhandler"
    modelname="job"
    modeldb=q.apps.system.jobhandler.models.job
    res=modeldb.find(params.query)
    if len(res)>100:
        params.result="TOO MANY RESULTS, MAX 100"
    else:
        params.result=res
    return params

def match(q,args,params,tags,tasklet):
    return True
