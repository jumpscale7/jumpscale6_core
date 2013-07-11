
from pylabs import q
import copy

class Master():
    def __init__(self):
        self.inited=False
        self.gridmap=None
        self.gridmapPrevious=None

    def _init(self):
        if self.inited==False:
            self.model=q.apps.system.master.models.gridmap
            if not self.model.exists(1):
                self.gridmap=self.model.new()
                self.model.set(self.gridmap)
            else:
                self.gridmap=self.model.get(1)
            self.gridmapPrevious=copy.copy(self.gridmap)
            q.core.appserver6.runningAppserver.gridmap=self.gridmap
            self.inited=True

    def gridMapGetRedisClusterFromIp(self,ip,port):
        for item in self.gridmap.redisclusters:
            for host in item.hosts:
                print host
                ip2,port2=host.split(":")
                if ip2==ip and port2==port:
                    return item
        return False

    def gridMapGetRedisClusterFromAppActorName(self,appname,actorname):
        key="%s__%s" % (appname,actorname)
        if self.gridmap.actor2redis.has_key(key):
            id=self.gridmap.actor2redis[key]
            return self.gridmap.redisclusters[id-1]
        return False

    def gridMapSave(self):
        if str(self.gridmapPrevious)<>str(self.gridmap):
            print "new gridmap"
            self.gridmap.version+=1
            self.model.set(self.gridmap)
            self.gridmapPrevious=copy.copy(self.gridmap)

    def gridMapGetAppserver(self,ipaddr,port):
        for appserver in self.gridmap.appservers:
            if appserver.host.find(":")==-1:
                raise RuntimeError("error in gridmap, appserverdef %s corrupt, host needs to be x:y notation" % appserver.host)
            ipaddr2,port2=appserver.host.split(":")
            if ipaddr2==ipaddr and port2==port:
                return appserver
        return False

    def gridMapGetActorInstance(self,appname,actorname,instance):
        key="%s__%s__%s" % (appname,actorname,instance)
        if self.gridmap.actorinstances.has_key(key):
            return self.gridmap.actorinstances[key]
        return False

    def gridMapRegisterAppserver(self,ismaster,ipaddr,port,secret):
        if self.gridMapGetAppserver(ipaddr, port) ==False:
            appserver=self.gridmap.new_appserver()
        else:
            appserver=self.gridMapGetAppserver(ipaddr, port)
        appserver.lastnotified=q.base.time.getTimeEpoch()
        appserver.start=q.base.time.getTimeEpoch()
        appserver.secret=secret
        appserver.host="%s:%s" % (ipaddr,port)
        if ismaster:
            self.gridmap.master="%s:%s" % (ipaddr,port)

    def gridMapRegisterActor(self,appname,actorname,instance,appserverHost,redisHost,arakoonHost):
        if self.gridMapGetActorInstance(appname,actorname,instance) ==False:
            actor=self.gridmap.new_actorinstance()
            actor.id=len(self.gridmap.actorinstances)-1
        else:
            actor=self.gridMapGetActorInstance(appname,actorname,instance)

        appsip,appsport=appserverHost.split(":")
        appserver=self.gridMapGetAppserver(appsip,appsport)
        actor.appserverid=appserver.id

        rip,rport=redisHost.split(":")
        r=self.gridMapGetRedisClusterFromIp(rip,rport)
        actor.redisclusterid=r.id

        actor.start=q.base.time.getTimeEpoch()

        if ismaster:
            self.gridmap.master="%s:%s" % (ipaddr,port)




