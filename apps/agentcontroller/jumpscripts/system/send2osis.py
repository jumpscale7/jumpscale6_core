from JumpScale import j

descr = """
send all gathered statistics to carbon (backend of monitoring)
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.send2carbon"
period = 10#120 #always in sec
enable=True
async=False
roles = ["osis.db.graphite"]

def action():
    stats = list()
    for key, stat in j.system.stataggregator.stats.iteritems():
        if stat.memonly:
            continue
        avg, mag = stat.getAvgMax()
        stats.append({'key': key, 'value': avg})
    if stats:
        j.processmanager.cache.statobject.osis.set(stats)

