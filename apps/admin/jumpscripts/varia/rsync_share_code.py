
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
    c.package_install_apt("rsync")
    C="""
motd file = /etc/rsyncd/rsyncd.motd
log file = /var/log/rsyncd.log
pid file = /var/run/rsyncd.pid
lock file = /var/run/rsync.lock
strict modes = false

[code]
   path = /opt/code
   comment = code
   uid = root
   gid = root
   read only = no
   list = no
   strict modes = false
   hosts allow = 
    """
    # from IPython import embed
    # print "DEBUG NOW yyy"
    # embed()
    raise RuntimeError("not finished yet")
            
