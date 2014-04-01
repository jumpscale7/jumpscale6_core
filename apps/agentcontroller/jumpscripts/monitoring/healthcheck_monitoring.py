from JumpScale import j
import time

descr = """
Monitor worker status
"""

organization = "jumpscale"
name = 'healthcheck_monitoring'
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "monitor.healthcheck"

period = 120 #always in sec
enable = True
async = True
roles = ["*"]


def action():
    import JumpScale.grid.gridhealthchecker
    nodeid = j.application.whoAmI.nid
    if nodeid == j.core.grid.healthchecker.masternid:
        results, errors = j.core.grid.healthchecker.checkProcessManagerAllNodes()
        if errors:
            for nid in errors:
                j.events.opserror('ProcessManager on node %s seems to have timed out' % nid, 'monitoring')
        results, errors = j.core.grid.healthchecker.checkElasticSearch()
        if errors:
            for nid in errors:
                j.events.opserror('ElasticSearch on node %s is not running' % nid, 'monitoring')
