from JumpScale import j

descr = """
This jumpscript echos back (test)
"""

name = "echo"
category = "test"
organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = []

period = 10 #always in sec
order = 1
enable=True
async=True
queue='process'
log=False

def action():
    msg="alive"
    print msg
