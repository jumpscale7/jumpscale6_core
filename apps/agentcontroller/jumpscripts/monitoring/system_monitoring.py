from JumpScale import j
import re


descr = """
gather statistics about system
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.processes"
period = 30 #always in sec
enable=True
async=True
queue='process'
log=False

roles = []

def action():
    if not hasattr(j.core, 'processmanager'):
        import JumpScale.grid.processmanager
        j.core.processmanager.loadMonitorObjectTypes()
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


    stat = j.system.fs.fileGetContents('/proc/stat')
    stats = dict()
    for line in stat.splitlines():
        _, key, value = re.split("^(\w+)\s", line)
        stats[key] = value

    num_ctx_switches = int(stats['ctxt'])

    results["cpu.num_ctx_switches"]=num_ctx_switches

    result2={}
    for key in results.keys():
        if key.find("percent")<>-1 or key.find("time")<>-1:
            percent=True
        else:
            percent=False
        if any([ x in key for x in ['network.', 'time', 'cpu.num'] ]):
            ttype="D"
        else:
            ttype="N"

        result2[key]=j.system.stataggregator.set("n%s.system.%s"%(j.application.whoAmI.nid,key),results[key],remember=True,memonly=False,percent=percent,ttype=ttype)

    return results


