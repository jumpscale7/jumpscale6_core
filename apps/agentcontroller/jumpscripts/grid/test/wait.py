from JumpScale import j
import time

descr = """
This jumpscript waits 30 sec (test)
"""

name = "wait"
category = "test"
organization = "opencode"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(msg,timeout):
    time.sleep(timeout)
    o.logger.log(msg, level=5, category="test.wait")
    return msg



