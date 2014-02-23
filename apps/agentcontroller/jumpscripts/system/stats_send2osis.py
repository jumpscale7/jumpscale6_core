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
enable=False
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
        try:
            #where does this come from???
            j.processmanager.cache.statobject.osis.set(stats)
        except Exception,e:
            if str(e).find("Connection refused")<>-1:
                j.events.opserror_critical("cannot forward stats to osis, there is probably no carbon running on osis", category='processmanager.send2osis.stats', e=None)
            j.errorconditionhandler.processPythonExceptionObject(e)            

