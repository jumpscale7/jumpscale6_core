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
enable=False

def action():
    
    osis=j.processmanager.cache.processobject.osis
    psutil=j.system.platform.psutil
    result={}

    j.processmanager.childrenPidsFound={}

    def send2osis(pid,processOsisObject):
        if pid<>0:
            process=j.processmanager.cache.processobject.get(pid) #is cached so low overhead

            process.getTotalsChildren()

            processOsisObject.gid=j.application.whoAmI.gid
            processOsisObject.nid=j.application.whoAmI.nid

            process.getTotalsChildren()

            #get all stats from the process in osis            
            for name in j.processmanager.cache.processobject.getProcessStatProps(True):
                if name.find("nr")==0 or name.find("cpu")==0 or name.find("mem")==0:
                    processOsisObject.__dict__[name]=process.__dict__[name]
                else:
                    processOsisObject.__dict__[name]=0.0
            
            guid,new,changed=osis.set(processOsisObject)
            process.guid=guid
            result[pid]=process
                                    

    for process in j.processmanager.startupmanager.manager.getProcessDefs():
        pid=process.getPid()
        print pid
        if pid:
            processOsisObject=osis.new()
            processOsisObject.active=process.isRunning()
            processOsisObject.name=process.name
            processOsisObject.systempid=pid
            processOsisObject.epochstart=0
            processOsisObject.jpname=process.jpackage_name
            processOsisObject.jpdomain=process.jpackage_domain
            processOsisObject.ports=process.ports
            processOsisObject.cmd=process.cmd
            processOsisObject.workingdir=process.workingdir
            send2osis(pid,processOsisObject)
            
    else:
        # plist=psutil.get_process_list()
        initprocess=j.system.process.getProcessObject(1)  #find init process

        for process in initprocess.get_children():
            if process.name in ["getty"]:
                continue
            pid = process.pid
            if pid == 0:
                continue

            print "systemprocess:%s %s"%(process.name, pid)

            if int(pid) not in result.keys():
                processOsisObject=osis.new()
                processOsisObject.active=False
                processOsisObject.jpname=""
                processOsisObject.jpdomain=""
                # process=j.processmanager.cache.processobject.get(process.pid)
                processOsisObject.cmd=" ".join(process.cmdline)
                processOsisObject.workingdir=""

                send2osis(pid,processOsisObject)



    for pid in j.processmanager.cache.processobject.monitorobjects.keys():
        #result is all found processobject in this run
        if pid and not result.has_key(pid):
            #no longer active
            print "NO LONGER ACTIVE"
            process=j.processmanager.cache.processobject.get(pid) #is cached so low overhead
            
            if not j.processmanager.cache.processobject.monitorobjects.get(pid).guid:
                j.processmanager.cache.processobject.monitorobjects.pop(pid)
                continue
            processOsisObject=osis.get(process.guid)

            processOsisObject.active=False

            for name in j.processmanager.cache.processobject.getProcessStatProps(True):
                processOsisObject.__dict__[name]=0.0

            osis.set(processOsisObject)    

            j.processmanager.cache.processobject.monitorobjects.pop(pid)
    j.processmanager.cache.processobject.monitorobjects=result



