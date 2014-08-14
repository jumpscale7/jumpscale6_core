from JumpScale import j

descr = """
creates a new desktop for a user
"""

name = "desktopcreate"
category = "desktop"
organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["desktop.server"]



def action(username,passwd):
    src="/home/_guest"
    dest="/home/%s"%username
    

    import JumpScale.baselib.remote

    cl = j.remote.cuisine.api
    j.remote.cuisine.fabric.env["password"]=j.application.config.get("system.superadmin.passwd")

    cl.connect("127.0.0.1")    

    j.logger.log("copy %s to %s"%(src,dest))
    j.system.fs.copyDirTree(src,dest)

    j.logger.log("create user %s"%username)
    cl.user_ensure(username,passwd,"/home/%s"%username)

    j.logger.log("user rights on home dir")
    j.system.process.execute("chown -R %s:%s %s"%(username,"root",dest))

    hrdcontent="user=%s\n"%username

    j.system.fs.createDir("%s/.jumpscale/"%src)

    j.logger.log("write hrd for home dir")
    hrdpath="%s/.jumpscale/.config.hrd"%src
    j.system.fs.writeFile(hrdpath,hrdcontent)

    hrd=j.core.hrd.getHRD(hrdpath)

    j.logger.log("apply hrd config in home dir")
    hrd.applyOnDir(dest)

    return "OK"



