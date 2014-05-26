from JumpScale import j

descr = """
deploy grid master
"""

organization = "jumpscale"
author = "hendrik@vscalers.com/kristof"
license = "bsd"
version = "1.0"
category = "debug.gridmaster"
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

    c.run("jpackage install -n grid_master_singlenode -r")


