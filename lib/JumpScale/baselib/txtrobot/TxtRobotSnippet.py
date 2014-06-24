from JumpScale import j
import hashlib
import ujson as json

class TxtRobotSnippet(object):  
    def __init__(self):
        self.redis = j.clients.redis.getRedisClient("localhost",7768)


    def create(self, snippet, robot):
        md5 = hashlib.md5(snippet).hexdigest()
        snippetinfo = {'snippet': snippet, 'robot': robot}
        self.redis.hset("robot.secrets", md5, json.dumps(snippetinfo))
        return md5


    def get(self, md5checksum):
        snippetinfo = json.loads(self.redis.hget("robot.secrets", md5checksum))
        snippet = snippetinfo['snippet']
        robotname = snippetinfo['robot']

        if 'youtrack' in robotname:
            import JumpScale.lib.youtrackclient
            robot = j.tools.youtrack.getRobot("http://incubaid.myjetbrains.com/youtrack/")
            output = robot.process(snippet)
        elif 'machine' in robotname:
            import JumpScale.lib.ms1
            robot = j.tools.ms1robot.getRobot()
            output = robot.process(snippet)

        return output
