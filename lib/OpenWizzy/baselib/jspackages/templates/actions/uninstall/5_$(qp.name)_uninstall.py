def main(q,args,params,tags,tasklet):
   
    #install the required files onto the system
    # can happen by e.g. installing a debian package e.g. by
    ## o.system.platformtype.ubuntu.install(packagename) 
    # can happen by copying files from the owpackage included files (they come from the bundle) e.g. by
    
    params.owpackage.removeFiles() #  will remove files known to owpackages
        
    #configuration is not done in this step !!!!!
    
    params.result=True #return True if result ok
    return params
    
    
def match(q,args,params,tags,tasklet):
    return True
