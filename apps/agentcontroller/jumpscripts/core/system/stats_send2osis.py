from JumpScale import j

descr = """
send all gathered statistics to carbon (backend of monitoring)
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.send2osis.carbon"
period = 10#120 #always in sec
enable=True
async=True
queue='process'
log = False
roles = []

def action():
    stats = list()
    for key, stat in j.system.stataggregator.stats.iteritems():
        if stat.memonly:
            continue
        avg, mag = stat.getAvgMax()
        stats.append([key,avg])
    OSISclient = j.core.osis.client
    if stats:
        try:
            OSISclientStat=j.core.osis.getClientForCategory(OSISclient,"system","stats")
            OSISclientStat.set(stats)
        except Exception,e:
            j.errorconditionhandler.processPythonExceptionObject(e)
            if str(e).find("Connection refused")<>-1:
                j.events.opserror_critical("cannot forward stats to osis, there is probably no carbon running on osis", category='processmanager.send2osis.stats', e=None)
