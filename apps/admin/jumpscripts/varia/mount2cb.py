
from JumpScale import j

descr = """
mount code dir to cloudbroker
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.mount.cloudbroker"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = True

def action(node):
    c=node.cuapi
    o=c.run("mount")
    nfs=False
    
    node.executeCmds("umount /opt/code/jumpscale",die=False)

    if o.find("172.16.131.1:/opt/code on /opt/code")<>-1:
        if c.dir_exists("/opt/code/jumpscale/unstable__jumpscale_core"):
            nfs=True
        else:
            node.executeCmds("umount /opt/code/jumpscale",die=False)
            node.executeCmds("umount /opt/code",die=False)
    
    if not nfs:
        c.package_install_apt("nfs-common")
        if not c.dir_exists("/opt/code2"):
            c.run("mv /opt/code /opt/code2")
        c.run("mkdir -p /opt/code/jumpscale")
        node.executeCmds("umount /opt/code/jumpscale",die=False)
        c.run("mount -t nfs 172.16.131.1:/opt/code /opt/code")

    fstab=c.file_read("/etc/fstab")

    fstab2=""
    for line in fstab.split("\n"):
        if line.find("172.16.131.1")<>-1:
            continue
        fstab2+="%s\n"%line

    l="172.16.131.1:/opt/code /opt/code nfs ro,hard,intr,noexec 0 0"
    fstab2+="%s\n"%l
    
    c.file_write("/etc/fstab",fstab2)
    
  
