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
roles = ["*"]



def action(username,passwd):
    src="/home/_guest"
    dest="/home/%s"%username
    

    import JumpScale.baselib.remote

    cl = j.remote.cuisine.api
    j.remote.cuisine.fabric.env["password"]=j.application.config.get("system.superadmin.passwd")

    cl.connect("127.0.0.1")    

    j.system.fs.copyDirTree(src,dest)

    cl.user_ensure(username,passwd,"/home/%s"%username)

    j.system.process.execute("chown -R %s %s %s"%(username,"root",dest))

    hrdcontent="user=%s\n"%user

    j.system.fs.createDir("%s/.jumpscale/"%src)

    hrdpath="%s/.jumpscale/.config.hrd"%src
    j.system.fs.writeFile(hrdpath,hrdcontent)

    hrd=j.core.hrd.getHRD(hrdpath)

    hrd.applyOnDir(dest)

    return msg



