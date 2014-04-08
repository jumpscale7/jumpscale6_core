
import credis
#see https://github.com/yihuang/credis

from JumpScale import j
import JumpScale.baselib.redis

from .CRedisQueue import CRedisQueue

#code https://github.com/yihuang/credis/blob/master/credis/base.pyx


class CRedisFactory:

    """
    """

    def __init__(self):
        self.redis = {}
        self.redisq = {}

    def getRedisClient(self, ipaddr, port,timeout=None):
        key = "%s_%s" % (ipaddr, port)
        if not self.redis.has_key(key):
            self.redis[key] = CRedis(ipaddr, port,timeout=timeout)
        return self.redis[key]

    def getRedisQueue(self, ipaddr, port, name, namespace="queues"):
        key = "%s_%s_%s_%s" % (ipaddr, port, name, namespace)
        if not self.redisq.has_key(key):
            self.redisq[key] = CRedisQueue(self.getRedisClient(ipaddr, port), name, namespace=namespace)
        return self.redisq[key]


class CRedis():
    """
    example for pipeline
     self.redis.execute_pipeline(('SET',"test","This Should Return"),('GET',"test"))
    """

    def __init__(self, addr="127.0.0.1",port=7768,timeout=None):
        self.redis=credis.Connection(host=addr,port=port,socket_timeout=timeout)
        self.redis.connect()            
        self.fallbackredis=j.clients.redis.getRedisClient(addr,port)
        #certain commands (which are not performance sensitive need normal pyredis)

    def llen(self,key):
        return self.redis.execute('LLEN',key)

    def rpush(self,key, item):
        return self.redis.execute('RPUSH',key,item)

    def blpop(self,key, timeout="60"): #@todo timeout?
        return self.redis.execute('BLPOP',key,0)

    def lpop(self,key):
        return self.redis.execute('LPOP',key)

    def exists(self,key):
        return self.redis.execute('EXISTS',key)
        
    def get(self,key):
        return self.redis.execute('GET',key)

    def set(self,key,value):
        return self.redis.execute('SET',key,value)

    def incr(self,key):
        return self.redis.execute('INCR',key)

    def incrby(self,key,nr):
        return self.redis.execute('INCRBY',key,nr)

    def delete(self,key):
        return self.redis.execute('DEL',key)

    def expire(self,key,timeout):
        return self.redis.execute('EXPIRE',key,timeout)

    def scriptload(self,script):
        return self.fallbackredis.script_load(script)
        # return self.redis.execute('SCRIPTLOAD',script)

    def evalsha(self,sha,nrkeys,*args):
        return self.redis.execute('EVALSHA',sha,nrkeys,*args)

    def eval(self,script,nrkeys,*args):        
        return self.redis.execute('EVAL',script,nrkeys,*args)
        
        

