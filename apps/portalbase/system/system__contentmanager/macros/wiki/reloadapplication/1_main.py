def main(o,args,params,tags,tasklet):
    params.merge(args)
    
    #temporary hack to get the application name
    name = o.system.fs.getParentDirName(o.system.fs.getParent(o.core.portal.runningPortal.webserver.cfgdir))
    o.core.portal.runningPortal.restartInProcess(name)

    params.result=("",params.doc)

 

def match(o,args,params,tags,tasklet):
    return True

