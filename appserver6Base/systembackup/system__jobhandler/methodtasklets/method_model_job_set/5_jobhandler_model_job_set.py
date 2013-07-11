
def main(q,args,params,tags,tasklet):
    #set
    #appname="system"
    #actorname="jobhandler"
    #modelname="job"
    modeldb=q.apps.system.jobhandler.models.job

    ddict=q.tools.json.decode(params.data)
    obj=modeldb.new()
    obj2=q.core.osis.dict2pymodelobject(obj,ddict)
    modeldb.set(obj2)
    params.result=[obj2.id,obj2.guid]
    return params

def match(q,args,params,tags,tasklet):
    return True
