
from JumpScale import j

descr = """
clean environment from past & install development jumpscale env
example:
jsexec -n debug_deploy_reset_jumpscale -s -f -o world -r sm1,sm2,sm3
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.js.core.clean.development"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):

    c=node.cuapi
    CMDS="""
killall tmux  #dangerous
killall redis-server
rm -rf /usr/local/lib/python2.7/dist-packages/jumpscale*
rm -rf /usr/local/lib/python2.7/site-packages/jumpscale*
rm -rf /usr/local/lib/python2.7/dist-packages/JumpScale*
rm -rf /usr/local/lib/python2.7/site-packages/JumpScale*
rm -rf /usr/local/lib/python2.7/site-packages/JumpScale/
rm -rf /usr/local/lib/python2.7/site-packages/jumpscale/
rm -rf /usr/local/lib/python2.7/dist-packages/JumpScale/
rm -rf /usr/local/lib/python2.7/dist-packages/jumpscale/
rm -rf /opt/jumpscale
rm /usr/local/bin/js*
rm /usr/local/bin/jpack*
killall python
rm -rf /opt/sentry/
sudo stop redisac
sudo stop redisp
sudo stop redism
sudo stop redisc
killall redis-server
rm -rf /opt/redis/
apt-get update
apt-get upgrade -y
apt-get install mercurial ssh python2.7 python-requests python-apt openssl ca-certificates python-pip ipython -y
"""
    
    node.executeCmds(CMDS, die=False,insandbox=False)

    CMDS="""
pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip
jpackage mdupdate
jpackage install -n base -r --debug
jpackage install -n core -r --debug
"""
    node.executeCmds(CMDS, die=True,insandbox=False)


