from JumpScale import j
import JumpScale.grid
import gevent
import unittest

PORT = 10777

class ControllerCMDS():
    def __init__(self, daemon):
        self.daemon = daemon

    def echo(self, msg, session):
        print msg
        gevent.sleep(1)
        return msg

def startServer():
    daemon = j.core.zdaemon.getZDaemon(port=PORT, name='test')
    daemon.setCMDsInterface(ControllerCMDS, category="agent")
    daemon.start()

class TEST(unittest.TestCase):
    def setUp(self):
        self.server = gevent.Greenlet(startServer)
        self.server.start()
        gevent.sleep(1) # give server some process time

    def tearDown(self):
        self.server.kill()

    def test_multiplecalls(self):
        cl = j.core.zdaemon.getZDaemonClient('127.0.0.1', port=PORT, category='agent', gevent=True)
        def makeCall():
            cl.echo('test')

        greenlets = list()
        for x in xrange(5):
            grn = gevent.Greenlet(makeCall)
            grn.start()
            greenlets.append(grn)
        gevent.joinall(greenlets, raise_error=True)
