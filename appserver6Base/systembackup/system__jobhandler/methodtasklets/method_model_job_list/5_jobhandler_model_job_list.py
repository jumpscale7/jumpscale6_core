
def main(q,args,params,tags,tasklet):
    #list
    from pylabs.Shell import ipshellDebug,ipshell
    print "DEBUG NOW model list"
    ipshell()
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
