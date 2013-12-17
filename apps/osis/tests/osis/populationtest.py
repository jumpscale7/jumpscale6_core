import unittest
import re
import time
from JumpScale import j
import random

import JumpScale.grid.osis

class OSISPopulationTest(unittest.TestCase):

    def setUp(self):
        print 'setup'
        self.client = j.core.osis.getClient()

    def tearDown(self):
        pass

    def test_1(self):
        from IPython import embed
        print "DEBUG NOW ooo"
        embed()
        

        self.prefix = time.time()
        # We make some basic entries to search on
        numbers = range(10)
        self.created = []
        for i in numbers:
            macaddr = randomMAC()
            netaddr = {macaddr: ['127.0.0.1', '127.0.0.2']}
            machineguid = j.tools.hash.md5_string(str(netaddr.keys()))
            obj = j.core.grid.zobjects.getZNodeObject(name="%s_%s" %
                                                     (self.prefix, i), netaddr=netaddr, machineguid=
                                                      machineguid)
            key, new, changed = client.set("system", "znode", obj)
            self.created.append(key)        
        
        print result


if __name__ == '__main__':
    unittest.main()
