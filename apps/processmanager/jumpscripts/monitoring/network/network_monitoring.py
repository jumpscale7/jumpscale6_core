from JumpScale import j

descr = """
gather statistics about system
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.nic"
period = 30 #always in sec
enable=True

def action():
    psutil=j.system.platform.psutil
    nodeid = j.application.whoAmI.nid

    netinfo=j.system.net.getNetworkInfo()

    # #network counters
    counters=psutil.network_io_counters(True)
    nr=0
    for key,nic in j.processmanager.nics.iteritems():

        if key in counters.keys():
            
            counter=counters[key]

            results={}

            bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout=counter
            results["network.kbytes.recv"]=round(bytes_recv/1024,0)
            results["network.kbytes.send"]=round(bytes_sent/1024,0)
            results["network.packets.recv"]=packets_recv
            results["network.packets.send"]=packets_sent
            results["network.error.in"]=errin
            results["network.error.out"]=errout
            results["network.drop.in"]=dropin
            results["network.drop.out"]=dropout

            for key in results.keys():
                j.system.stataggregator.set("n%s.i%s.%s"%(nodeid, nic.id,key),results[key],remember=True)




