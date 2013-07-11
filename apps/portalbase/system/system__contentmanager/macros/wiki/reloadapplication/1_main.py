def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    #temporary hack to get the application name
    name = q.system.fs.getParentDirName(q.system.fs.getParent(q.core.appserver6.runningAppserver.webserver.cfgdir))
    q.core.appserver6.runningAppserver.restartInProcess(name)

    params.result=("",params.doc)

 

def match(q,args,params,tags,tasklet):
    return True

