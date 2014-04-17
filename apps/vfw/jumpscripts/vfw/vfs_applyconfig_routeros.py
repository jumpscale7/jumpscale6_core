from JumpScale import j
import JumpScale.baselib.remote

descr = """
Applies the rules in the passed fwobject to the given LXC machine name
"""

name = "vfs_applyconfig_routeros"
category = "vfw"
organization = "jumpscale"
author = "hendrik@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["vfw.host"]
async = True 

def action(name, fwobject):
    from JumpScale.lib import routeros

    host = fwobject['host']
    username = fwobject['username']
    password = fwobject['password']

    ro = routeros.RouterOS.RouterOS(host, username, password)
    ro.deletePortForwardRules(tags='cloudbroker')
    for rule in fwobject['tcpForwardRules']:  
        ro.addPortForwardRule(rule['fromAddr'], rule['fromPort'], rule['toAddr'], rule['toPort'], tags='cloudbroker')
    return True
