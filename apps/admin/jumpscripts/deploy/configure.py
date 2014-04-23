
from JumpScale import j

descr = """
update platform with some local config files
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.platform.uploadconfig"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):
    node.uploadFromCfgDir("jscfg","$basedir/cfg/")
    node.uploadFromCfgDir("etc","/etc/")
    node.uploadFromCfgDir("root","/root/")

    #cmd="jsconfig hrdset -n system.superadmin.passwd -v %s"%node.args.passwd
    #print node.cuapi.run(cmd)            

