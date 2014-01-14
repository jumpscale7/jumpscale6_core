from JumpScale import j

descr = """
tell stat aggregator to cleanup history
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.aggregate"
period = 120 #always in sec
enable=True

def action():
    j.system.stataggregator.clean()


