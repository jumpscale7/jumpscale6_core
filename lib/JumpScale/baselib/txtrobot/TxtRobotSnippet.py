from JumpScale import j
import hashlib
import ujson as json

class TxtRobotSnippet(object):  
    def __init__(self):
        self.redis = j.clients.redis.getRedisClient("localhost",7768)


    def create(self, snippet):
        md5 = hashlib.md5(snippet).hexdigest()
        self.redis.hset("robot.secrets", md5, json.dumps(snippet))
        return md5


    def get(self, md5checksum):
        snippet = json.loads(self.redis.hget("robot.secrets", md5checksum))
        return snippet
