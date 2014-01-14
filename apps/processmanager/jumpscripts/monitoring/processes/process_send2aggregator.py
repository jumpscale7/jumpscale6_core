from JumpScale import j

descr = """
gather statistics about processes, and store in stataggregator
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.processes"
period = 20 #always in sec
enable=True

def action():
    for process_key,obj in j.processmanager.cache.processobject.monitorobjects.iteritems():
        results=obj.getStatInfo(totals=True)
        for key, value in results.iteritems():            
            j.system.stataggregator.set("n%s.%s.%s"%(j.application.whoAmI.nid,process_key,key),value,remember=True)

#check behaviour in http://localhost:8081/

