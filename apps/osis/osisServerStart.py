#this must be in the beginning so things are patched before ever imported by other libraries
from gevent import monkey
#monkey.patch_all()
monkey.patch_socket()
monkey.patch_thread()
monkey.patch_time()
#gevent.monkey.patch_sys(stdin=True, stdout=True, stderr=True)

from JumpScale import j
import JumpScale.grid.osis
import time

j.application.start("osisserver")


import sys

args=sys.argv
argstag=" ".join(args[1:])
connections=j.core.tags.getObject(argstag).getDict()
connections2={}

#example to start osis : 
#cd /opt/jsbox/apps/osis;python osisServerStart.py elasticsearch:main mongodb:main

for jpackagename,instancename in connections.iteritems():
    if jpackagename in ["influxdb"]:
        domain="serverapps"
    else:
        domain="jumpscale"
    jp=j.packages.findNewest(name="%s_client"%jpackagename,domain=domain)
    jp=jp.getInstance(instancename)
    if not jp.isInstalled():
        j.events.opserror_critical("cannot start osis, db connection %s was not available, please install."%jpackagename)
    hrd=jp.hrd_instance
    if hrd==None:
        j.events.opserror_critical("cannot start osis, db connection %s was not available, please install & configure properly, did not find active hrd."%jpackagename)
    
    print "connect to: %s"%jpackagename

    if jpackagename=="elasticsearch":
        import JumpScale.baselib.elasticsearch
        ipaddr=hrd.get("es.client.addr")
        port=hrd.getInt("es.client.port")
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)        
            print "cannot connect to elasticsearch, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.elasticsearch.get(ip=ipaddr, port=port, timeout=60)

    elif jpackagename=="mongodb":
        import JumpScale.grid.mongodbclient
        ipaddr=hrd.get("mongodb.client.addr")
        port=hrd.getInt("mongodb.client.port")    
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)
            print "cannot connect to mongodb, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.mongodb.get(host=ipaddr, port=port)

    elif jpackagename=="redis":
        import JumpScale.baselib.redis
        ipaddr=hrd.get("redis.client.addr")
        port=hrd.getInt("redis.client.port")        
        passwd=hrd.get("redis.client.passwd")
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)
            print "cannot connect to redis, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.redis.getGeventRedisClient(ipaddr, port, fromcache=True, password=passwd)

    elif jpackagename=="influxdb":
        import JumpScale.baselib.influxdb
        ipaddr=hrd.get("influxdb.client.addr")
        port=hrd.getInt("influxdb.client.port")        
        login=hrd.get("influxdb.client.login")
        passwd=hrd.get("influxdb.client.passwd")
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)
            print "cannot connect to influxdb, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        
        client=j.clients.influxdb.get(host=ipaddr, port=port,username=login, password=passwd, database="main")

        # data = [{"points":[[1.1,4.3,2.1],[1.2,2.0,2.0]],"name":"web_devweb01_load","columns":["min1", "min5", "min15"]}]
        # client.write_points(data)
        

    client.hrd=hrd #remember hrd as well
    
    connections2["%s_%s"%(jpackagename,instancename)]=client

j.core.osis.startDaemon(path="", overwriteHRD=False, overwriteImplementation=False, key="",port=5544,superadminpasswd=None,dbconnections=connections2)

j.application.stop()
