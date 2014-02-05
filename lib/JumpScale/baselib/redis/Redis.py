from JumpScale import j

import geventredis
import redis
from geventredis.RedisQueue import RedisQueue


class RedisFactory:
    """
    """

    def __init__(self):
        self.gredis={}
        self.redis={}
        # self.gredisq={}
        # self.redisq={}

    def getGeventRedisClient(self,ipaddr,port):
        key="%s_%s"%(ipaddr,port)
        if not self.gredis.has_key(key):
            self.gredis[key]=geventredis.connect(ipaddr, port)
        return self.gredis[key]

    def getRedisClient(self,ipaddr,port):
        key="%s_%s"%(ipaddr,port)
        if not self.redis.has_key(key):
            self.redis[key]=redis.Redis(ipaddr, port)
        return self.redis[key]

    def getRedisQueue(self,ipaddr,port,name,namespace="queues"):
        return RedisQueue(self.getRedisClient(ipaddr,port),name,namespace=namespace)

    def getGeventRedisQueue(self,ipaddr,port,name,namespace="queues"):
        return RedisQueue(self.getGeventRedisClient(ipaddr,port),name,namespace=namespace)


