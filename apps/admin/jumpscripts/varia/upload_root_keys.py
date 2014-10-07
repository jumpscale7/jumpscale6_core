
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

    tags=j.core.tags.getObject(node.args.extra)

    basepath=j.dirs.replaceTxtDirVars(j.application.config.get("admin.basepath"))
    d = j.system.fs.joinPaths(basepath, 'identities')
    if not j.system.fs.exists(path=d):
        raise RuntimeError("cannot find basepath:%s"%d)

    if str(tags)<>"":
        #only use system key
        username=str(tags)
        u = j.system.fs.joinPaths(basepath, 'identities',username)
        filename = j.system.fs.joinPaths(u, 'id.hrd')
        hrd=j.core.hrd.getHRD(filename)
        pkey=hrd.get("id.key.dsa.pub")
        keys.append(pkey)
        print "Found", len(keys), "public system ssh keys"
        if str(tags)=="system":
            for name in ["id_dsa","id_dsa.pub"]:
                u = j.system.fs.joinPaths(basepath, 'identities',username,name)
                j.system.fs.copyFile(u,"/root/.ssh/%s"%name)
                j.system.fs.chmod("/root/.ssh/%s"%name,384)
    else:
        # Fetch keys from repo
        for filename in j.system.fs.listFilesInDir(d, recursive=True, filter='*id.hrd'):
            hrd=j.core.hrd.getHRD(filename)
            pkey=hrd.get("id.key.dsa.pub")
            keys.append(pkey)
        print "Found", len(keys), "public ssh keys"

    #Remove current keys ##DEFAULT SHOULD NOT DO THIS
    # cuapi.run("rm -f /root/.ssh/authorized_keys")

    #Put new keys
    for key in keys:
        print key
        print cuapi.ssh_authorize('root', key)
        print "key added"

