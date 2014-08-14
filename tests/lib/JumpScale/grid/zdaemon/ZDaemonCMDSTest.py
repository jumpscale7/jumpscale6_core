import unittest

from gridlib.zdaemon.ZDaemonCMDS import ZDaemonCMDS


class CMDS(ZDaemonCMDS):

    """
    Class with some sample functions used to test the generation of the ZDaemonCMDS methods
    """

    def __init__(self, daemon):
        ZDaemonCMDS.__init__(self, daemon)

    def myTestFunction(self, paramA='a', session=None, paramB='b'):
        pass


class ZDaemonCMDSTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testZDaemonCMDS_introspect_removes_session(self):
        methods = CMDS(None)._introspect(None)
        self.assertListEqual(methods['myTestFunction']['args'][0], ['self', 'paramA', 'paramB'])
        self.assertTupleEqual(methods['myTestFunction']['args'][3][-2:], ('a', 'b'))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
