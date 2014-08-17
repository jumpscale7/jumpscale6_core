
from JumpScale import j

import JumpScale.grid.zdaemon

j.application.start("pertest")

def test():
    #some to be tested code
    pass 

import JumpScale.baselib.performancetrace

j.tools.performancetrace.profile('test()', globals=globals())


j.application.stop()
