from JumpScale import j

descr = """
gather statistics about system
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.processes"
period = 10 #always in sec
enable=False

def action():
	psutil=j.system.platform.psutil
    results={}
    nr=0
    val=psutil.cpu_percent(0)
    results["cpu.percent"]=round(val,0)
    cput= psutil.cpu_times()
    for key in cput.__dict__.keys():
        val=cput.__dict__[key]
        results["cpu.time.%s"%(key)]=val

    counter=psutil.network_io_counters(False)
    bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout=counter
    results["network.kbytes.recv"]=round(bytes_recv/1024,0)
    results["network.kbytes.send"]=round(bytes_sent/1024,0)
    results["network.packets.recv"]=packets_recv
    results["network.packets.send"]=packets_sent
    results["network.error.in"]=errin
    results["network.error.out"]=errout
    results["network.drop.in"]=dropin
    results["network.drop.out"]=dropout


    total,used,free,percent=psutil.phymem_usage()
    results["memory.free"]=round(free/1024/1024,2)
    results["memory.used"]=round(used/1024/1024,2)
    results["memory.percent"]=percent

    total,used,free,percent,sin,sout=psutil.virtmem_usage()
    results["swap.free"]=round(free/1024/1024,2)
    results["swap.used"]=round(used/1024/1024,2)
    results["swap.percent"]=percent

    result2={}
    for key in results.keys():
        result2[key]=j.system.stataggregator.set("n%s.%s"%(j.application.whoAmI.nid,key),results[key],remember=True)

    return results


