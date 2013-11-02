def main(j,args,params,tags,tasklet):
   
    #install the required files onto the system

    # can happen by e.g. installing a debian package e.g. by
    ## j.system.platform.ubuntu.install(packagename)
       
    ##args.jp.copyFiles(subdir="root",destination="/",applyhrd=True) #  will copy files from subdir called root of platforms to root of system (carefull), will also use templateEngine for hrd 

    ##copy python libs: then need to be in subdir site-packages of one of the platforms, they will all be copied to site-packages in local python dir
    #args.jp.copyPythonLibs(remove=False)

    #install found debs they need to be in debs dir of one or more of the platforms (all relevant platforms will be used)
    #args.jp.installUbuntuDebs()
    
    #shortcut to some usefull install tools
    #do=j.system.installtools

    #make sure app starts by using circus, make sure circus jpackage is installed (normally it is (-:))
    #j.tools.circus.manager.addProcess(name, cmd, args='', warmup_delay=0, numprocesses=1, priority=0, autostart=True)

    #configuration is not done in this step !!!!!
    
    params.result=True #return True if result ok
    return params
    
    
def match(j,args,params,tags,tasklet):
    return True
