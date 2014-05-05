
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
        print c.run("pip uninstall JumpScale-core -y")
        print c.run("rm -rf /opt/jumpscale")
        print c.run("rm -rf /usr/local/lib/python2.7/dist-packages/JumpScale*")
        print c.run("rm /usr/bin/jspython")
    except:
        pass
    print c.run("cd /usr/bin;ln -s python jspython")
    print c.run("pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip")
    print c.run("pip install ujson")
    
    node.uploadFromCfgDir("jscfg","/opt/jumpscale/cfg/")

    print c.run("jpackage mdupdate")
    print c.run("jpackage install -n base -r --debug")

    print c.run("jpackage install -n core -r --debug")
    print c.run("jpackage install -n redis -r")
