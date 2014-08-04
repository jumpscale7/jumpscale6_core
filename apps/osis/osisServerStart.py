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
    jp=j.packages.findNewest(name="%s_client"%jpackagename,domain="jumpscale")
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
        port=hrd.get("es.client.port")
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)        
            print "cannot connect to elasticsearch, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.elasticsearch.get(ip=ipaddr, port=port, timeout=60)

    elif jpackagename=="mongodb":
        import JumpScale.grid.mongodbclient
        ipaddr=hrd.get("mongodb.client.addr")
        port=hrd.get("mongodb.client.port")    
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)
            print "cannot connect to mongodb, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.mongodb.get(host=ipaddr, port=port)

    elif jpackagename=="redis":
        import JumpScale.baselib.redis
        ipaddr=hrd.get("redis.client.addr")
        port=hrd.get("redis.client.port")        
        passwd=hrd.get("redis.client.passwd")
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)
            print "cannot connect to redis, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.redis.getGeventRedisClient(ipaddr, port, fromcache=True, password=passwd)

    elif jpackagename=="influxdb":
        import JumpScale.baselib.redis
        ipaddr=hrd.get("redis.client.addr")
        port=hrd.get("redis.client.port")        
        passwd=hrd.get("redis.client.passwd")
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)
            print "cannot connect to redis, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.redis.getGeventRedisClient(ipaddr, port, fromcache=True, password=passwd)        

    client.hrd=hrd #remember hrd as well
    
    connections2["%s_%s"%(jpackagename,instancename)]=client

j.core.osis.startDaemon(path="", overwriteHRD=False, overwriteImplementation=False, key="",port=5544,superadminpasswd=None,dbconnections=connections2)

j.application.stop()
