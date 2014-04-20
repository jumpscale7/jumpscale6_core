
from JumpScale import j

descr = """
Fetches the public keys from the vscalers_sysadmin repo and puts them in authorized_keys

use '-e system '  to only use the system key (e.g. in production env on a mgmt node)
"""

organization = "vscalers"
author = "tim@incubaid.com"
license = "bsd"
version = "1.0"
category = "ssh.keys.upload"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):
    keys = []
    cuapi=node.cuapi

    from IPython import embed
    print "DEBUG NOW ooo"
    embed()
    

    # Fetch keys from repo
    basepath=j.dirs.replaceTxtDirVars(j.application.config.get("admin.basepath"))
    d = j.system.fs.joinPaths(basepath, 'identities')
    if not j.system.fs.exists(path=d):
        raise RuntimeError("cannot find basepath:%s"%d)
    for u in j.system.fs.listDirsInDir(d):
        filename = j.system.fs.joinPaths(u, 'id.hrd')
        hrd=j.core.hrd.getHRD(filename)
        pkey=hrd.get("id.key.dsa.pub")
        keys.append(pkey)
    print "Found", len(keys), "public ssh keys"

    #Remove current keys
    cuapi.run("rm -f /root/.ssh/authorized_keys")

    #Put new keys
    for key in keys:
        print key
        cuapi.ssh_authorize('root', key)

