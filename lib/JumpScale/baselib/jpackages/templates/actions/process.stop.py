def main(jp):
   
    #stop the application (only relevant for server apps)
    
    jp.log("stop $(jp.name)")
    j.tools.startupmanager.stopJPackage(jp)

    jp.waitDown(timeout=20)


