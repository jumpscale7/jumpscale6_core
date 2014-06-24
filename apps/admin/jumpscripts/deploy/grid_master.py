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
    c.run('''debconf-set-selections <<< "postfix postfix/mailname string your.hostname.com"''')
    c.run('''debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"''')
    #print c.run("jpackage install -n postgresql -r")
    #print c.run("jpackage install -n sentry -r")
    #print c.run("jsprocess start -n sentry")
    c.run("jpackage install -n elasticsearch -r")
    c.run("jpackage install -n rediskvs_master -r")
    c.run("jpackage install -n graphite -r")
    c.run("jsprocess start -n graphite")
    c.run("jpackage install -n portal -r --debug")
    c.run("jpackage install -n osis -r --debug -s")
    c.run("jpackage install -n grid_master -r --debug")
