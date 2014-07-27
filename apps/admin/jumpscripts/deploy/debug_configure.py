
from JumpScale import j

descr = """
update platform with some local config files
example
jsexec -n debug_configure -c kds -s -o world -r sm1,sm2,sm3
e.g. /opt/jumpscale/apps/admin/cfgs/kds/jscfg/ needs to exist (jscfg will be copied to jumpscale cfg dir)
the hrd will be applied in it (put as template  $(varname)  )
also $(hostname) is available to be replaced

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
    #can add additional template vars in
    node.cuapi.run("rm -rf /opt/jumpscaledir")
    node.uploadFromCfgDir("jscfg","$base/cfg/",additionalArgs={})
    node.uploadFromCfgDir("etc","/etc/")
    node.uploadFromCfgDir("root","/root/")

    #cmd="jsconfig hrdset -n system.superadmin.passwd -v %s"%node.args.passwd
    #print node.cuapi.run(cmd)            

