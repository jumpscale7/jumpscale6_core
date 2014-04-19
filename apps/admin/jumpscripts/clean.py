
from JumpScale import j

descr = """
clean environment from past
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.js.core.clean"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):

    c=node.cuapi
    CMDS="""
killall tmux
rm -rf /usr/local/lib/python2.7/dist-packages/jumpscale.pth
rm -rf /usr/local/lib/python2.7/site-packages/JumpScale/
rm -rf /usr/local/lib/python2.7/site-packages/jumpscale/
rm -rf /usr/local/lib/python2.7/dist-packages/JumpScale/
rm -rf /usr/local/lib/python2.7/dist-packages/jumpscale/
rm -rf /opt/code
rm -rf /opt/jumpscale
rm /usr/local/bin/js*
rm /usr/local/bin/jpack*
killall python
killall redis-server
rm -rf /opt/sentry/
rm -rf /opt/redis/
"""
    for line in CMDS.split("\n"):
        if line.strip()<>"" and line[0]<>"#":
            try:
                print c.run(line)
            except:
                pass
