def main(jp):
   
    #start the application (only relevant for server apps)
    jp.log("start $(jp.name)")
    j.tools.startupmanager.startJPackage(jp)
    jp.waitUp(timeout=20)

