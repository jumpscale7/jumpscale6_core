from JumpScale import j

descr = """
echo (return mesg)
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "tools.echo.sync"
period = 12*3600 #every 12h restart full process
enable=False
startatboot=False
async=False
roles = ["*"]

def action(msg=""):
    return msg