#from JumpScale import j

import time

def testf(r):
    time.sleep(0.1)
    raise RuntimeError("error")
    return r
