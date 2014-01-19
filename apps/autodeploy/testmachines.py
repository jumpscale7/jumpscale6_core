from JumpScale import j

j.application.appname = "installer"
j.application.start()



import JumpScale.baselib.remote


accounts=[]
accounts.append(["SamehGaballah","95.85.10.181",""])
accounts.append(["MahmoudAdel","95.85.15.25",""])
accounts.append(["MohamedGalal","95.85.15.29",""])
accounts.append(["DavidMichel","95.85.23.185",""])

passwd="r11t4r"

for name,remote,seedpasswd in accounts:

    print "#### WORK ON: %s %s"%(name,remote)

    #this will make sure new password is set
    #cl=j.tools.expect.new("sh")
    #cl.login(remote=remote,passwd=passwd,seedpasswd=seedpasswd,timeout=20)

    #setpasswd
    cuapi = j.remote.cuisine.api
    j.remote.cuisine.fabric.env["password"]=passwd
    cuapi.connect(remote)

    #print cuapi.apt_get("update")
    #print cuapi.apt_get("upgrade")
    #print cuapi.apt_get("install mercurial ssh python2.7 python-apt openssl ca-certificates python-pip ipython mc -y")
    
    # print cuapi.dir_ensure("/opt/jumpscale/cfgtest/jsconfig/", True)    
    # print cuapi.dir_ensure("/opt/jumpscale/cfgtest/jpackages/", True)
    # print cuapi.file_upload("/opt/jumpscale/cfgtest/jsconfig/blobstor.cfg","cfg/jsconfig/blobstor.cfg")
    # print cuapi.file_upload("/opt/jumpscale/cfgtest/jsconfig/bitbucket.cfg", "/opt/jumpscale/cfg/jsconfig/bitbucket.cfg")
    # print cuapi.file_upload("/opt/jumpscale/cfgtest/jpackages/sources.cfg","cfg/jpackages/sources.cfg")

    # print cuapi.run("jpackage_update")
    # print cuapi.run("jpackage_install -n shorewall -r")

    #cmd='update-rc.d xrdp defaults'
    #print cuapi.run(cmd)

    #sethostname
    #print cuapi.run("echo \"%s\" > /etc/hostname"%name)
    #print cuapi.run("reboot")

    # print cuapi.file_upload("/etc/shorewall/rules","fwtest/rules")
    # print cuapi.run("shorewall stop")
    # print cuapi.run("shorewall start")

    # print cuapi.file_upload("/etc/xrdp/xrdp.ini","xrdptest/xrdp.ini")
    # print cuapi.run("/etc/init.d/xrdp restart")
    print cuapi.run("/etc/init.d/xrdp start")

    print "#### DONE: %s %s\n\n\n"%(name,remote)


j.application.stop()


