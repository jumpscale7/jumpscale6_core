def main(j,args,params,tags,tasklet):
   
    #start the application (only relevant for server apps)
    #make sure you doublecheck that the app is really started (DO THIS CAREFULLY) e.g. check process & port if network daemon & eventually even a selftest in the app
    
    # import JumpScale.baselib.circus
    # args.jp.log("start osis")
    # j.tools.startupmanager.startProcess('osis')

    # args.jp.log("test if osis got started by doing a port test")
    # if j.system.net.waitConnectionTest("127.0.0.1",5544,20)==False:
    #     raise RuntimeError("Could not configure osis, osis did not start on port 5544.")
    
    params.result=True #return True if result ok
    return params
    
    
def match(j,args,params,tags,tasklet):
    return True