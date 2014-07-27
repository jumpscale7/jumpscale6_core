
from JumpScale import j

descr = """
update platform with jpackages
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.platform.update"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):
    cuapi=node.cuapi
    print cuapi.apt_get("update")    
    print cuapi.apt_get("upgrade")
    print cuapi.apt_get("install mercurial ssh curl python2.7 python-requests python-apt openssl ca-certificates python-pip python-dev ipython mc -y")
