from JumpScale import j

descr = """
This jumpscript throws error
"""

name = "wait"
category = "test"
organization = "opencode"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(msg):
    raise RuntimeError("test")
    return msg



