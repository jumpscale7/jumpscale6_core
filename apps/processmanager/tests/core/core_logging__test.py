from JumpScale import j

import JumpScale.grid.geventws
import JumpScale.baselib.redis

# j.application.start("test")

descr = """
see if basic logging works to redis & then being processed by process mgr
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "core.logging.basic"
enable=True
priority=5

class TEST():

    def setUp(self):
        #make sure logging happens
        self.serverip="127.0.0.1"
        print "check process manager active"
        if not j.system.net.tcpPortConnectionTest(self.serverip,4445) == True:
            j.errorconditionhandler.raiseOperationalCritical("could not connect to processmanager, is it running?", category="processmanager.test.setup")
        print "check redis active"
        if not j.system.net.tcpPortConnectionTest(self.serverip,7767) or not j.system.net.tcpPortConnectionTest(self.serverip,7768):
            j.errorconditionhandler.raiseOperationalCritical("could not connect to redis, is it running? (port 7767 and 7768)", category="processmanager.test.setup")
        print "check port elasticsearch"
        if not  j.system.net.tcpPortConnectionTest(self.serverip,9200):
            j.errorconditionhandler.raiseOperationalCritical("could not connect to elasticsearch, is it running? (port 9200)", category="processmanager.test.setup")
            
        self.client= j.servers.geventws.getClient("127.0.0.1", 4445, org="myorg", user=j.application.config.get('system.superadmin.login'), \
            passwd=j.application.config.get('grid.master.superadminpasswd'),category="jpackages")
        self.logqueue=j.clients.redis.getRedisQueue("127.0.0.1",7768,"logs")
        self.logqueueEco=j.clients.redis.getRedisQueue("127.0.0.1",7768,"eco")
        self.redis=j.clients.redis.getRedisClient("127.0.0.1",7768)
        j.logger.setLogTargetLogForwarder()


    def test_sendlog_checkredis(self):
        print "delete queues for logs"
        self.redis.delete("queues:logs")
        print "send 10 logs"
        for i in range(10):
            j.logger.log("a message",5,"my.cat","color:red important")
        print "lOGS DONE"

        ##only valid when testing redis only
        # print "check queue size"
        # assert self.logqueue.qsize()==10
        # print "queue size ok"
        # self.redis.delete("queues:logs")

        #check logs are in ES



    def test_sendeco_checkredis(self):
        print "delete queues for ecos"
        self.redis.delete("queues:eco")
        print "send 5 ecos"
        for i in range(5):
            try:
                print 1/0
            except Exception,e:
                j.errorconditionhandler.processPythonExceptionObject(e)

        ##only valid when testing redis only
        # print "check queue size eco"
        # assert self.logqueueEco.qsize()==5  
        # self.redis.delete("queues:eco")

        #check eco's are in ES        