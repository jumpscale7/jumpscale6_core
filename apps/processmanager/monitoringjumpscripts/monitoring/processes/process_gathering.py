from JumpScale import j

descr = """
gather statistics about system
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "info.gather.process"
period = 300 #always in sec
enable=True

def action():
    
    osis=j.processmanager.cache.processobject.osis
    psutil=j.system.platform.psutil
    result={}
    resultwitchchildren={}

    for process in j.processmanager.startupmanager.manager.getProcessDefs():
        pid=process.pid
        if pid<>0:
            process2=osis.new()
            if process.active==None:
                process.isRunning()
            process2.active=process.active
            process2.name=process.name
            process2.systempid=process.pid
            process2.epochstart=0
            process2.jpname=process.jpackage_name
            process2.jpdomain=process.jpackage_domain
            process2.ports=process.ports
            process2.cmd=process.cmd
            process2.workingdir=process.workingdir
            result[int(pid)]=process2

    else:
        # plist=psutil.get_process_list()
        initprocess=j.system.process.getProcessObject(1)  #find init process

        for process in initprocess.get_children():
            if process.name in ["getty"]:
                continue

            if process.pid==0:
                continue

            print "systemprocess:%s %s"%(process.name,process.pid)

            if int(process.pid) not in result.keys():
                process2=osis.new()
                process2.active=False
                process2.jpname=""
                process2.jpdomain=""
                # process=j.processmanager.cache.processobject.get(process.pid)
                process2.cmd=" ".join(process.cmdline)
                process2.workingdir=""

                pid=int(process.pid)

                result[pid]=process2

            
    for pid,process2 in result.iteritems():        
        if pid<>0:
            process=j.processmanager.cache.processobject.get(pid) #is cached so low overhead

            process2.gid=j.application.whoAmI.gid
            process2.nid=j.application.whoAmI.nid

            process.getTotalsChildren()

            #get all stats from the process in osis            
            for name in j.processmanager.cache.processobject.getProcessStatProps(True):
                if name.find("nr")==0 or name.find("cpu")==0 or name.find("mem")==0:
                    process2.__dict__[name]=process.__dict__[name]
                else:
                    process2.__dict__[name]=0.0
            
            guid,new,changed=osis.set(process2)
            process.guid=guid
            result[pid]=process


    for pid in j.processmanager.cache.processobject.monitorobjects.keys():
        if pid<>0 and pid not in result.keys():
            #no longer active
            print "NO LONGER ACTIVE"
            process=j.processmanager.cache.processobject.get(pid) #is cached so low overhead
            from IPython import embed
            print "DEBUG NOW ooo"
            embed()
            
            process2=osis.get(process.guid)

            process2.active=False

            for name in j.processmanager.cache.processobject.getProcessStatProps(True):
                process2.__dict__[name]=0.0

            osis.set(process2)    
                
            j.processmanager.cache.processobject.monitorobjects.pop(pid)

    j.processmanager.cache.processobject.monitorobjects=result



