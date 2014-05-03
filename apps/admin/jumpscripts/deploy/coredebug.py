
from JumpScale import j

descr = """
core jumpscale deployment in debug
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "deploy.js.core.debug"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):

    c=node.cuapi
    try:
        c.run("pip uninstall JumpScale-core -y")
        c.run("rm -rf /opt/jumpscale")
        c.run("rm -rf /usr/local/lib/python2.7/dist-packages/JumpScale*")
        c.run("rm /usr/bin/jspython")
    except:
        pass
    c.run("cd /usr/bin;ln -s python jspython")
    c.run("pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip")
    c.run("pip install ujson")

    node.uploadFromCfgDir("jscfg","/opt/jumpscale/cfg/")

    c.run("jpackage mdupdate")
    c.run("jpackage install -n base -r --debug")

    c.run("jpackage install -n core -r --debug")
    c.run("jpackage install -n redis -r")
