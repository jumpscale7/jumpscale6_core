from JumpScale import j

descr = """
send every X time the gathered stats to osis
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "process.send2osis"
period = 300 #always in sec
enable=True
async=False

def action():
    for process in j.processmanager.cache.processobject.monitorobjects.itervalues():
        process.send2osis()
        
