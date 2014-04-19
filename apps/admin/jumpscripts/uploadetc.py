
from JumpScale import j

descr = """
update platform with some local config files for etc
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.platform.uploadetc"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):
    c=node.cuapi
    c.file_unlink("/etc/resolv.conf")
    node.uploadFromCfgDir("etc","/etc/")
    node.uploadFromCfgDir("root","/root/")
