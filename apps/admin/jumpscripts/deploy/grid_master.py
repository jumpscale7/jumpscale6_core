from JumpScale import j

descr = """
deploy grid node
"""

organization = "jumpscale"
author = "hendrik@vscalers.com"
license = "bsd"
version = "1.0"
category = "deploy.gridnode"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


def action(node):

    c=node.cuapi
    print c.run('''debconf-set-selections <<< "postfix postfix/mailname string your.hostname.com"''')
    print c.run('''debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"''')
    #print c.run("jpackage install -n postgresql -r")
    #print c.run("jpackage install -n sentry -r")
    #print c.run("jsprocess start -n sentry")
    print c.run("jpackage install -n graphite -r")
    print c.run("jsprocess start -n graphite")
    print c.run("jpackage install -n elasticsearch -r")
    print c.run("jpackage install -n agentcontroller -r --debug")
    print c.run("jsprocess start -n agentcontroller")
    print c.run("jpackage install -n grid_master -r --debug")
    print c.run("jpackage install -n grid_node -r --debug")
    print c.run("jpackage install -n processmanager -r --debug")
    print c.run("jsprocess start -n processmanager")
    print c.run("jpackage install -n portal -r --debug")
    print c.run("jpackage install -n workers -r --debug")
    print c.run("jpackage install -n grid_portal")
    print c.run("jsprocess start -c")
