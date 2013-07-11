
def main(q,args,params,tags,tasklet):
    params.result=None

    je=q.apps.system.jobhandler.extensions.jobexecutor

    args=params.expandParamsAsDict(actormethod="",\
        defname="", \
        defcode="",\
        defpath="",\
        defagentid="",\
        name="",\
        category="",\
        errordescr="",\
        recoverydescr="",\
        maxtime="",\
        channel="",\
        location="",\
        user="",\
        wait="",\
        defargs={},
        defmd5="")    

    jobobj=je.getJobObjFromArgs(**args)

    je.scheduleNowWait(jobobj)

    return params

def match(q,args,params,tags,tasklet):
    return True
