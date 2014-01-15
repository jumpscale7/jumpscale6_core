

descr = """
gather statistics about machines
"""

organization = "jumpscale"
author = "deboeck@incubaid.com"
license = "bsd"
version = "1.0"
category = "info.gather.machines"
period = 300 #always in sec
enable = True

from JumpScale import j

def action():
    for machine in j.processmanager.cache.machineobject.monitorobjects.copy().itervalues():
        machine.cache.osis.set(machine.db)
