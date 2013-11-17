def main(j,jp):
   
    #kill the process
    jp.log("kill $(jp.name)")
    j.tools.startupmanager.killJPackage(jp)

    jp.waitDown(timeout=20)


