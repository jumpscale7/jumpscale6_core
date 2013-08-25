import unittest
from gridlib.zdaemon.ZDaemonCMDS import ZDaemonCMDS
from gridlib.zdaemon.ZDaemonClient import ZDaemonCmdClient
import mock


class CMDS(ZDaemonCMDS):

    """
    Class with some sample functions used to test the generation of the ZDaemonCMDClient
    """

    def __init__(self, daemon):
        ZDaemonCMDS.__init__(self, daemon)

    def myTestFunction(self, paramA=None):
        pass


@mock.patch('gridlib.zdaemon.ZDaemonClient.ZDaemonClient')
class ZDaemonCMDClientTest(unittest.TestCase):

    def setUp(self):
        # Generate spec
        self.spec = CMDS(None)._introspect(None)

    def tearDown(self):
        pass

    def testZDaemonCMDClientProxy_ArgsIsTuple(self, zdClientMock):
        # add tuple to spec
        self.spec['myTestFunction']['args'] = (('self', 'paramA'), None, None, (None,))

        zdClientMock.return_value.sendcmd.return_value = self.spec
        client = ZDaemonCmdClient()
        # Todo validate testfunction exists
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testZDeamonCMDClientProxy']
    unittest.main()
