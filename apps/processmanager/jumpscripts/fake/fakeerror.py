from JumpScale import j

descr = """
fake
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "fake.fake"
period = 1 #always in sec
enable=False
async=False

def action():
    raise RuntimeError("oef")
    return "HALLO"


