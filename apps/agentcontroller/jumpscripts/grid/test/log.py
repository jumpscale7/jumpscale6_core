from JumpScale import j

descr = """
This jumpscript logs something (test)
"""

name = "log"
category = "test"
organization = "opencode"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(msg):
    o.logger.log("test log msg", level=5, category="acategory")
    return msg



