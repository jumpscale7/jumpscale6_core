
from JumpScale import j

descr = """
update gridmaster from debug
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.security.perimeter"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = True

def action(node):
    raise RuntimeError("needs to be verified")
    c=node.cuapi
    node.uploadFromCfgDir("jscfgsecurity","/opt/jumpscale/cfg/")
    # c.run("jpackage install -n shorewall")
    c.run("apt-get install shorewall")
    c.run("shorewall clear")
    c.run("shorewall stop")
    c.run("jpackage install -n openvpn")
    c.run("apt-get install pptpd -y")
    c.run("jpackage install -n webmin")
    c.run("jsprocess disable -n openvpn")
    c.run("jsprocess status")
    c.run("/etc/init.d/webmin start")

