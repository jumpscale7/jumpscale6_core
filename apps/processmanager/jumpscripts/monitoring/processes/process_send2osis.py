from JumpScale import j

descr = """
send every X time the gathered stats to osis
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.send2osis"
period = 60 #always in sec
enable=True

def action():
    for process in j.processmanager.cache.processobject.monitorobjects.copy().itervalues():
        process.cache.osis.set(process.db)
