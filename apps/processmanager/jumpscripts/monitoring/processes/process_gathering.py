from JumpScale import j

descr = """
gather statistics about system
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "info.gather.process"
period = 30 #always in sec
enable=True

def action():

    result={}
    
    def loadFromSystemProcessInfo(cacheobj,pid):
        cacheobj.p=j.system.process.getProcessObject(pid)

        cacheobj.db.pname=cacheobj.p.name
        cacheobj.db.systempid=pid

        cacheobj.db.epochstart = cacheobj.p.create_time

        #MEMORY
        cacheobj.db.mem_rss,cacheobj.db.mem_vms=cacheobj.p.get_memory_info()

        connections= cacheobj.p.get_connections()
        if len(connections)>0:
            cacheobj.db.nr_connections=len(connections)
            for c in connections:
                if c.status=="LISTEN":
                    #is server
                    port=c.local_address[1]
                    if port not in cacheobj.ports:
                        cacheobj.db.ports.append(port)
                    if c.remote_address<>() and c.remote_address not in cacheobj.netConnectionsIn:
                        cacheobj.netConnectionsIn.append(c.remote_address)
                if c.status=="ESTABLISHED":
                    if c.remote_address not in cacheobj.netConnectionsOut:
                        cacheobj.netConnectionsOut.append(c.remote_address)

        cacheobj.db.nr_connections_in=len(cacheobj.netConnectionsIn)
        cacheobj.db.nr_connections_out=len(cacheobj.netConnectionsOut)

        cacheobj.db.io_read_count, cacheobj.db.io_write_count, cacheobj.db.io_read_bytes, cacheobj.db.io_write_bytes=cacheobj.p.get_io_counters()
        cacheobj.db.cmd=cacheobj.p.getcwd()
        cacheobj.db.parent=cacheobj.p.parent.pid
        cacheobj.db.nr_file_descriptors=cacheobj.p.get_num_fds()
        cacheobj.db.nr_ctx_switches_voluntary,cacheobj.db.nr_ctx_switches_involuntary=cacheobj.p.get_num_ctx_switches()
        cacheobj.db.nr_threads=cacheobj.p.get_num_threads()
        # cacheobj.nr_openfiles=cacheobj.p.get_open_files()
        cacheobj.db.cpu_time_user,cacheobj.db.cpu_time_system=cacheobj.p.get_cpu_times()
        cacheobj.db.cpu_percent=cacheobj.p.get_cpu_percent(0)
        cacheobj.db.user=cacheobj.p.username

        for child in cacheobj.p.get_children():
            if hasattr(child, 'pid'):
                childpid = child.pid
            else:
                childpid = child.getPid()
            child=j.processmanager.cache.processobject.get(childpid,child,lastcheck)
            if not j.processmanager.childrenPidsFound.has_key(childpid):                
                cacheobj.children.append(child)
                j.processmanager.childrenPidsFound[int(childpid)]=True



    #walk over startupmanager processes (make sure we don't double count)
    for sprocess in j.processmanager.startupmanager.manager.getProcessDefs():
        pid=process.getPid()
        print pid
        if pid:
            process_key="%s_%s"%(sprocess.domain,sprocess.name)

            exists=j.processmanager.cache.processobject.exists(process_key)

            cacheobj=j.processmanager.cache.processobject.get(id=process_key)
            processOsisObject=cacheobj.db

            processOsisObject.active=sprocess.isRunning()
            processOsisObject.ports = sprocess.ports
            processOsisObject.jpname = sprocess.jpackage_name
            processOsisObject.jpdomain=sprocess.jpackage_domain
            processOsisObject.workingdir = sprocess.workingdir
            processOsisObject.cmd = sprocess.cmd
            processOsisObject.sname = sprocess.name

            loadFromSystemProcessInfo(cacheobj,pid)

            process.getTotalsChildren()

            result[process_key]=cacheobj

            if exists==False: #first time store in osis (is when starting up)
                j.processmanager.cache.processobject.set(cacheobj)

    # plist=psutil.get_process_list()
    initprocess=j.system.process.getProcessObject(1)  #find init process

    for process in initprocess.get_children():
        if process.name in ["getty"]:
            continue
        pid = process.pid
        if pid == 0:
            continue

        print "systemprocess:%s %s"%(process.name, pid)

        process_key=process.name
        exists=j.processmanager.cache.processobject.exists(process_key)

        if result.has_key(process_key):
            #process with same name does already exist, lets first create temp getProcessObject
            cacheobj=j.processmanager.cache.processobject.get(id=pid)
        else:
            cacheobj=j.processmanager.cache.processobject.get(id=process_key)

        processOsisObject=cacheobj.db

        processOsisObject.active=True #process.is_running()

        processOsisObject.name=process.name

        processOsisObject.workingdir = process.getcwd()
        processOsisObject.cmd = process.exe
 
        process.getTotalsChildren()

        if result.has_key(process_key):
            #was double process, need to aggregate
            cacheobjPrev=result[process_key]
            #cacheobj+=...  aggregate with prev obj
            for item in j.processmanager.cache.processobject.getProcessStatProps():
                itemtot="%s_total"%item
                cacheobj.db.__dict__[item]+=float(cacheobjPrev.db.__dict__[item])    
                cacheobj.db.__dict__[itemtot]+=float(cacheobjPrev.db.__dict__[itemtot]) 
            #@todo NEED TO SEE FOR OTHER RELEVANT ITEMS TOO TO AGGREGATE
            cacheobj.db.id=process_key

        result[process_key]=cacheobj    

        if exists==False:
            j.processmanager.cache.processobject.set(cacheobj)



    #find deleted processes
    for process_key in j.processmanager.cache.processobject.monitorobjects.keys():
        #result is all found processobject in this run
        if process_key and not result.has_key(process_key):
            #no longer active
            print "NO LONGER ACTIVE"
            process=j.processmanager.cache.processobject.get(process_key) #is cached so low overhead

            processOsisObject=osis.get(process.guid)

            processOsisObject.active=False

            for name in j.processmanager.cache.processobject.getProcessStatProps(True):
                processOsisObject.__dict__[name]=0.0

            osis.set(processOsisObject)    

            j.processmanager.cache.processobject.monitorobjects.pop(process_key)
            
    j.processmanager.cache.processobject.monitorobjects=result



