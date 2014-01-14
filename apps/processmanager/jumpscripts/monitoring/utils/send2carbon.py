from JumpScale import j

descr = """
send all gathered statistics to carbon (backend of monitoring)
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.send2carbon"
period = 120 #always in sec
enable=True

def action():
    j.system.stataggregator.send2carbon()

