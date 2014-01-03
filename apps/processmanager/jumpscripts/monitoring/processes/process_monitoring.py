from JumpScale import j

descr = """
gather statistics about processes, and store in stataggregator
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.processes"
period = 10 #always in sec
enable=False

def action():
	
    for pid,obj in j.processmanager.cache.processobject.monitorobjects.iteritems():
        result=obj.getStatInfo(totals=True)
        for key in results.keys():
            j.system.stataggregator.set("n%s.p%s.%s"%(j.application.whoAmI.nid,obj.id,key),results[key],remember=True)


#check behaviour in http://localhost:8081/

