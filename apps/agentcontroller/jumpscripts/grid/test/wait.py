from JumpScale import j

descr = """
This jumpscript returns network info
"""

name = "wait"
category = "test"
organization = "opencode"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(msg):
    print msg

    # raise RuntimeError("test")

    return msg



