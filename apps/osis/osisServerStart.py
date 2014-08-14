#this must be in the beginning so things are patched before ever imported by other libraries
from gevent import monkey
#monkey.patch_all()
monkey.patch_socket()
monkey.patch_ssl()
monkey.patch_thread()
monkey.patch_time()


from JumpScale import j
import JumpScale.grid.osis
import time

j.application.start("osisserver")

import sys

args=sys.argv
osis_instance=args[1]

osisjp=j.packages.findNewest(name="osis",domain="jumpscale")
osisjp=osisjp.load(osis_instance)

argstag=" ".join(args[2:])
connectionsconfig = j.core.tags.getObject(argstag).getDict()
connections = {}

#example to start osis : 
#cd /opt/jsbox/apps/osis;python osisServerStart.py elasticsearch:main mongodb:main

for dbname, instancename in connectionsconfig.iteritems():
    if dbname in ["influxdb"]:
        domain="serverapps"
    else:
        domain="jumpscale"
    jp=j.packages.findNewest(name="%s_client"%dbname,domain=domain)
    jp=jp.load(instancename)
    if not jp.isInstalled():
        j.events.opserror_critical("cannot start osis, db connection %s was not available, please install."%dbname)
    hrd=jp.hrd_instance
    if hrd==None:
        j.events.opserror_critical("cannot start osis, db connection %s was not available, please install & configure properly, did not find active hrd."%dbname)

    print "connect to: %s"%dbname

    if dbname=="elasticsearch":
        import JumpScale.baselib.elasticsearch
        ipaddr=hrd.get("es.client.addr")
        port=hrd.getInt("es.client.port")
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)        
            print "cannot connect to elasticsearch, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.elasticsearch.get(ip=ipaddr, port=port, timeout=60)

    elif dbname=="mongodb":
        import JumpScale.grid.mongodbclient
        ipaddr=hrd.get("mongodb.client.addr")
        port=hrd.getInt("mongodb.client.port")    
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)
            print "cannot connect to mongodb, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.mongodb.get(host=ipaddr, port=port)

    elif dbname=="redis":
        import JumpScale.baselib.redis
        ipaddr=hrd.get("redis.client.addr")
        port=hrd.getInt("redis.client.port")        
        passwd=hrd.get("redis.client.passwd")
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)
            print "cannot connect to redis, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)
        client=j.clients.redis.getGeventRedisClient(ipaddr, port, fromcache=True, password=passwd)

    elif dbname=="influxdb":
        import JumpScale.baselib.influxdb
        ipaddr=hrd.get("influxdb.client.addr")
        port=hrd.getInt("influxdb.client.port")        
        login=hrd.get("influxdb.client.login")
        passwd=hrd.get("influxdb.client.passwd")
        while j.system.net.tcpPortConnectionTest(ipaddr,port)==False:
            time.sleep(0.1)
            print "cannot connect to influxdb, will keep on trying forever, please start (%s:%s)"%(ipaddr,port)

        client=j.clients.influxdb.get(host=ipaddr, port=port,username=login, password=passwd, database="main")

    client.hrd=hrd #remember hrd as well
    
    connections["%s_%s"%(dbname,instancename)]=client

superadminpasswd=osisjp.hrd_instance.get("osis.superadmin.passwd")

j.core.osis.startDaemon(path="", overwriteHRD=False, overwriteImplementation=False, key="",port=5544,superadminpasswd=superadminpasswd,dbconnections=connections,hrd=osisjp.hrd_instance)

j.application.stop()
