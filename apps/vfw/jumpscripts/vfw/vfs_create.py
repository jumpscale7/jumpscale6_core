from JumpScale import j
import JumpScale.lib.lxc
import JumpScale.baselib.remote

descr = """
Creates an LXC machine from template
"""

name = "vfs_create"
category = "vfw"
organization = "jumpscale"
author = "zains@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["vfw.host"]


def action(name, base):
    templatespath = j.system.fs.joinPaths('/opt', 'lxc', 'templates')
    j.system.platform.lxc.createMachine(name=name, base=j.system.fs.joinPaths(templatespath, base))
    j.system.platform.lxc.start(name)
    ipaddress = j.system.platform.lxc.getIp(name)
    remoteApi = j.remote.cuisine.api
    #assuming template password is rooter
    j.remote.cuisine.fabric.env['password'] = 'rooter'
    remoteApi.connect(ipaddress)
    status = remoteApi.run('service ssh status')
    if 'running' not in status:
        j.errorconditionhandler.raiseOperationalWarning("SSH is not running on machine '%s'" % name)
    #set root password


