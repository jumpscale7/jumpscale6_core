from JumpScale import j

import geventredis
import redis
from .geventredis.RedisQueue import RedisQueue


class RedisFactory:
    """
    """

    def __init__(self):
        self.gredis={}
        self.redis={}
        self.gredisq={}
        self.redisq={}

    def getGeventRedisClient(self,ipaddr,port, fromcache=True):
        if not fromcache:
            return geventredis.connect(ipaddr, port)
        key="%s_%s"%(ipaddr,port)
        if key not in self.gredis:
            self.gredis[key]=geventredis.connect(ipaddr, port)
        return self.gredis[key]

    def getRedisClient(self,ipaddr,port):
        key="%s_%s"%(ipaddr,port)
        if not self.redis.has_key(key):
            self.redis[key]=redis.Redis(ipaddr, port)
        return self.redis[key]

    def getRedisQueue(self,ipaddr,port,name,namespace="queues"):
        key="%s_%s_%s_%s"%(ipaddr,port,name,namespace)
        if not self.redisq.has_key(key):
            self.redisq[key]=RedisQueue(self.getRedisClient(ipaddr,port),name,namespace=namespace)
        return self.redisq[key]

    def getGeventRedisQueue(self,ipaddr,port,name,namespace="queues"):
        key="%s_%s_%s_%s"%(ipaddr,port,name,namespace)
        if not self.gredisq.has_key(key):
            self.gredisq[key]=RedisQueue(self.getGeventRedisClient(ipaddr,port),name,namespace=namespace)
        return self.gredisq[key]        


