from JumpScale import j
import JumpScale.grid.geventws
cl = j.servers.geventws.getClient('localhost', 8888, 'example')

import JumpScale.baselib.performancetrace

def perftest():
    print "start"
    for i in range(100):
        cl.ping()
    print "stop"


# res=j.tools.performancetrace.profile('perftest()', globals=globals())

