from JumpScale import j

descr = """
This jumpscript echos back (test)
"""

name = "echo"
category = "test"
organization = "opencode"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(msg):
    print msg
    return msg



